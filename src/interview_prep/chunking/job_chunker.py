"""File for chunking job descriptions into meaningful sections."""

from ast import List
from typing import Any, Dict
from interview_prep.schemas.cv_schema import JobDescriptionChunk, Document
from constants import JOB_DESCRIPTION_SECTION_HEADERS
from interview_prep.utils.text_tools import sentence_based_chunking
from interview_prep.chunking.base_chunker import BaseChunker


class JobChunker(BaseChunker):

    def parse_sections(self, document: Document):
        """Parse Job Description into sections like Responsibilities, Requirements."""
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

        self.sections = sections
    
    def parse_as_one_section(self, document: Document):
        """Parse job description as only one section, removing empty lines and extra spaces."""
        section = {
            "section": "Full Job Description",
            "content": [line.strip() for line in document.normalized_text.split("\n") if line.strip()],
            "lines": list(range(len(document.normalized_text.split("\n")))),
            "id": 0,
        }
        self.sections = [section]

    def chunk_sections(self):
        """Convert Job Description sections into fine-grained JobDescriptionChunk objects."""
        chunks = []
        chunk_id = 0
        for section in self.sections:
            section_text = ' '.join(section['content'])
            sentence_chunks = sentence_based_chunking(section_text, chunk_size=300, overlap=50)
            for chunk_text in sentence_chunks:
                chunks.append(JobDescriptionChunk(
                    id=chunk_id,
                    text=chunk_text,  # Changed from 'content' to 'text'
                    section=section['section'],
                    chunk_type="ITEM"  # Added required field
                ))
                chunk_id += 1
        print(f"Created {len(chunks)} chunks from {len(self.sections)} sections.")
    
        self.chunks = chunks

            