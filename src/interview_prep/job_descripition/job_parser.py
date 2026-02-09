"""File to parse job descriptions."""
from constants import JOB_DESCRIPTION_SECTION_HEADERS, TECHNICAL_SKILLS, TASKS, EXCLUDE, REQUIREMENT_KEYWORDS
from interview_prep.schemas.cv_schema import Document, JobDescriptionChunk
from interview_prep.utils.text_tools import normalize_text, normalize_chunk_text
from pathlib import Path
from typing import List

class JobDescriptionParser:
    """Class to parse job descriptions."""
    def __init__(self):
        pass

    def parse_description(self, job_description_file: str):
        """Parse a job description file and return a Document model."""

        text = ""
        with Path.open(job_description_file, "r") as f:
            text = f.read()

        normalized_text = normalize_text(text)
        doc = Document(category="Job Description",
                       raw_text=text,
                       normalized_text=normalized_text,
                       source=job_description_file)

        return doc
    
    def _create_sections(self, document: Document) -> List[dict]:
        #manual chunking
        sections = []
        current_section = {
            "section": "Introduction",
            "content": [],
            "lines": [],
            "id": 0,
        }

        for i, line in enumerate(document.normalized_text.split("\n")):
            
            if not line.strip():
                continue
            
            #checking main section headers
            if line in JOB_DESCRIPTION_SECTION_HEADERS or len(line.split()) < 5:
                # Save current section if it has content
                if current_section["content"] or current_section["lines"]:
                    sections.append(current_section)
                
                current_section = {
                    "section": line.strip(),
                    "content": [],
                    "lines": [i],
                    "id": len(sections),
                }
            
            else:
                current_section["content"].append(line.strip())
                current_section["lines"].append(i)
        
        # Don't forget the last section
        if current_section["content"] or current_section["lines"]:
            sections.append(current_section)
        
        print(f"\nCreated {len(sections)} sections:\n")
        
        for index, s in enumerate(sections):
            content_text = ' '.join(s['content'])
            print(f"Section {index}:")
            print(f"Header: {s['section']}")
            print(f"Content length: {len(content_text)} chars")
            if s['lines']:
                print(f"Lines: {min(s['lines'])} - {max(s['lines'])}")
            print(f"Preview: {content_text[:150]}...")
            print("\n")
        
        return sections

    def chunk_description(self, document: Document, max_chunk_size: int = 500) -> List[JobDescriptionChunk]:
        """Chunk a job description document.
        
        - Consecutive empty sections are combined into a single chunk with their titles
        - Sections with content are split into chunks of max_chunk_size characters
        - Each content chunk includes the section title
        """
        sections = self._create_sections(document)
        
        chunks = []
        chunk_id = 0
        empty_sections_buffer = []
        
        for section in sections:
            # If section has no content, add to buffer
            if len(section["content"]) == 0:
                empty_sections_buffer.append(section["section"])
                continue
            
            #create a chunk from empty sections
            if empty_sections_buffer:
                combined_title = " ".join(empty_sections_buffer)
                chunks.append(JobDescriptionChunk(
                    id=chunk_id,
                    text=combined_title,
                    section="Metadata",
                    chunk_type="HEADER",
                ))
                chunk_id += 1
                empty_sections_buffer = []

            # handle non empty content
            section_title = section["section"]
            full_content = " ".join(section["content"])
            
            # If content fits in one chunk
            if len(full_content) <= max_chunk_size:
                chunk_text = f"{section_title}\n\n{full_content}"
                chunks.append(JobDescriptionChunk(
                    id=chunk_id,
                    text=normalize_chunk_text(chunk_text),
                    section=section_title,
                    chunk_type="CONTENT",
                ))
                chunk_id += 1
            else:
                # Split content into smaller chunks
                words = full_content.split()
                current_chunk_words = []
                current_length = 0
                
                for word in words:
                    word_length = len(word) + 1  # +1 for space
                    
                    if current_length + word_length > max_chunk_size and current_chunk_words:
                        # Create chunk with current words
                        chunk_content = " ".join(current_chunk_words)
                        chunk_text = f"{section_title}\n\n{chunk_content}"
                        chunks.append(JobDescriptionChunk(
                            id=chunk_id,
                            text=normalize_chunk_text(chunk_text),
                            section=section_title,
                            chunk_type="CONTENT"
                        ))
                        chunk_id += 1
                        current_chunk_words = [word]
                        current_length = word_length
                    else:
                        current_chunk_words.append(word)
                        current_length += word_length
                
                # Don't forget last chunk
                if current_chunk_words:
                    chunk_content = " ".join(current_chunk_words)
                    chunk_text = f"{section_title}\n\n{chunk_content}"
                    chunks.append(JobDescriptionChunk(
                        id=chunk_id,
                        text=normalize_chunk_text(chunk_text),
                        section=section_title,
                        chunk_type="CONTENT"
                    ))
                    chunk_id += 1
        
        # Handle any remaining empty sections at the end
        if empty_sections_buffer:
            combined_title = " | ".join(empty_sections_buffer)
            chunks.append(JobDescriptionChunk(
                id=chunk_id,
                text=combined_title,
                section="Metadata",
                chunk_type="HEADER"
            ))
        
        print(f"\n✓ Created {len(chunks)} chunks from {len(sections)} sections\n")
        
        for chunk in chunks:
            print(f"Chunk {chunk.id}: Section='{chunk.section}', Type={chunk.chunk_type}, Length={len(chunk.text)} chars")
            print(f"Preview: {chunk.text[:100]}...")
            print()
        
        self.chunks = chunks
    
    def select_relevant_chunks(self):
        """Select the most relevant chunks for the job description.
        
        Scores chunks based on:
        - Presence of requirements keywords from config
        - Presence of task verbs from config
        - Presence of technical skills from config
        - Absence of exclude keywords from config
        
        Returns chunks sorted by relevance score.
        """
        scored_chunks = []
        
        for chunk in self.chunks:
            score = 0
            text_lower = chunk.text.lower()
            
            # Check for requirements keywords (weight: 2)
            for keyword in REQUIREMENT_KEYWORDS:
                if keyword.lower() in text_lower:
                    score += 2
            
            # Check for task verbs (weight: 3)
            for task in TASKS:
                if task.lower() in text_lower:
                    score += 3
            
            # Check for technical skills (weight: 5)
            for skill in TECHNICAL_SKILLS:
                if skill.lower() in text_lower:
                    score += 5
            
            # Penalize for exclude keywords (weight: -10)
            for exclude_word in EXCLUDE:
                if exclude_word.lower() in text_lower:
                    score -= 5
            
            # Boost score if chunk type is already marked as relevant
            
            scored_chunks.append({
                "chunk": chunk,
                "score": score
            })
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        # Print summary
        print(f"\n✓ Scored {len(scored_chunks)} chunks:\n")
        for item in scored_chunks:
            chunk = item["chunk"]
            score = item["score"]
            print(f"Chunk {chunk.id} | Score: {score:3d} | Type: {chunk.chunk_type} | Section: {chunk.section}")
            print(f"Preview: {chunk.text[:80]}...")
            print()
        
        return scored_chunks
            


            

