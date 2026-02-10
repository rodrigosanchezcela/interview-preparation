"""File to parse job descriptions."""
from constants import JOB_DESCRIPTION_SECTION_HEADERS, TECHNICAL_SKILLS, TASKS, EXCLUDE, REQUIREMENT_KEYWORDS
from interview_prep.schemas.cv_schema import Document, JobDescriptionChunk
from interview_prep.utils.text_tools import normalize_text, normalize_chunk_text
from config import config
from pathlib import Path
from pathlib import Path
from typing import List
from interview_prep.schemas.cv_schema import CVChunk
import re

class JobDescriptionParser:
    """Class to parse job descriptions."""
    def __init__(self):
        self.chunks: List[JobDescriptionChunk] = []
        self.document: Document | None = None

    def parse_description(self, job_description_file: str):
        """Parse a job description file and return a Document model."""

        text = ""
        with Path.open(job_description_file, "r") as f:
            text = f.read()

        normalized_text = normalize_text(text)
        doc = Document(category="Job Description",
                       raw_text=text,
                       normalized_text=normalized_text,
                       source=job_description_file,
                       )

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
                    chunk_type="HEADING",
                ))
                chunk_id += 1
                empty_sections_buffer = []

            # handle non empty content
            section_title = section["section"]
            full_content = " ".join(section["content"])
            
            # If content fits in one chunk
            if len(full_content) <= max_chunk_size:
                chunk_text = f"{section_title} {full_content}"
                chunks.append(JobDescriptionChunk(
                    id=chunk_id,
                    text=normalize_chunk_text(chunk_text),
                    section=section_title,
                    chunk_type="ITEM",
                ))
                chunk_id += 1
            else:
                # Split content into smaller chunks at sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', full_content)
                current_chunk_sentences = []
                current_length = 0
                
                for sentence in sentences:
                    sentence_length = len(sentence) + 1  # +1 for space
                    
                    if current_length + sentence_length > max_chunk_size and current_chunk_sentences:
                        # Create chunk with current sentences
                        chunk_content = " ".join(current_chunk_sentences)
                        chunk_text = f"{section_title} {chunk_content}"
                        chunks.append(JobDescriptionChunk(
                            id=chunk_id,
                            text=normalize_chunk_text(chunk_text),
                            section=section_title,
                            chunk_type="ITEM"
                        ))
                        chunk_id += 1
                        current_chunk_sentences = [sentence]
                        current_length = sentence_length
                    else:
                        current_chunk_sentences.append(sentence)
                        current_length += sentence_length
                
                # Don't forget last chunk
                if current_chunk_sentences:
                    chunk_content = " ".join(current_chunk_sentences)
                    chunk_text = f"{section_title} {chunk_content}"
                    chunks.append(JobDescriptionChunk(
                        id=chunk_id,
                        text=normalize_chunk_text(chunk_text),
                        section=section_title,
                        chunk_type="ITEM"
                    ))
                    chunk_id += 1
        
        # Handle any remaining empty sections at the end
        if empty_sections_buffer:
            combined_title = " | ".join(empty_sections_buffer)
            chunks.append(JobDescriptionChunk(
                id=chunk_id,
                text=combined_title,
                section="Metadata",
                chunk_type="HEADING",
            ))
        
        print(f"\n✓ Created {len(chunks)} chunks from {len(sections)} sections\n")
        
        for chunk in chunks:
            print(f"Chunk {chunk.id}: Section='{chunk.section}', Type={chunk.chunk_type}, Length={len(chunk.text)} chars")
            print(f"Preview: {chunk.text[:100]}...")
            print()
        
        self.chunks = chunks
        self.document = document
        return chunks
    
    def select_relevant_chunks(self, min_score: int = 0, chunk_types: List[str] = None) -> List[JobDescriptionChunk]:
        """Select the most relevant chunks for the job description.
        
        Args:
            min_score: Minimum score threshold for selection (default: 0)
            chunk_types: Optional list of chunk types to consider. If None, considers all types except HEADER
        
        Scores chunks based on:
        - Presence of requirements keywords from config
        - Presence of task verbs from config
        - Presence of technical skills from config
        - Absence of exclude keywords from config
        
        Returns chunks sorted by relevance score.
        """
        if not self.chunks:
            return []
        
        if chunk_types is None:
            chunk_types = ["ITEM", "HEADING"]  # Exclude HEADER by default
        
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
        
        # Filter by chunk type and minimum score, keeping track of scores for sorting
        filtered_with_scores = [
            item for item in scored_chunks 
            if item["chunk"].chunk_type in chunk_types and item["score"] >= min_score
        ]
        
        # Sort by score descending
        filtered_with_scores.sort(key=lambda x: x["score"], reverse=True)

        
        # Return just the chunks (like CVChunker does)
        return [item["chunk"] for item in filtered_with_scores]
    
    def save_chunks(self, output_dir: Path | None = None):
        """Save chunks to JSON file.
        
        Args:
            output_dir: Optional custom output directory. Defaults to config.processed_data_dir/job_descriptions
        """
        import json
        
        if not self.chunks:
            print("No chunks to save")
            return
        
        if not self.document:
            print("No document loaded")
            return
        
        if output_dir is None:
            output_dir = config.processed_data_dir / "job_descriptions"
        
        Path.mkdir(output_dir, parents=True, exist_ok=True)
        
        # Get filename from document source
        source_filename = Path(self.document.source).stem
        output_file = output_dir / f"{source_filename}_chunks.json"
        
        chunks_data = [chunk.model_dump() for chunk in self.chunks]
        
        with open(output_file, 'w') as f:
            json.dump(chunks_data, f, indent=2)
        
        print(f"Saved {len(self.chunks)} chunks to {output_file}")
    
    def process_job_description(self, job_file: str, save: bool = True, max_chunk_size: int = 500) -> List[JobDescriptionChunk]:
        """Complete pipeline: parse, chunk, and optionally save.
        
        Args:
            job_file: Path to job description file
            save: Whether to save chunks to file
            max_chunk_size: Maximum size of content chunks
            
        Returns:
            List of job description chunks
        """
        document = self.parse_description(job_file)
        chunks = self.chunk_description(document, max_chunk_size)
        
        if save:
            self.save_chunks()
        
        return chunks
    
    def reset(self):
        """Reset state for processing a new job description."""
        self.chunks = []
        self.document = None
        

            


            

