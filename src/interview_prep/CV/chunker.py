
from interview_prep.schemas.cv_schema import Document, CVChunk
from constants import CV_SECTION_HEADERS, TECHNICAL_SKILLS
import json
from config import config
from pathlib import Path
from typing import List
import os
import sys


class CVChunker:
    """Class to chunk CVs into small items."""
    def __init__(self):
        self.chunks: List[CVChunk] = []
        self.document: Document | None = None

    def _retrieve_sections(self, document: Document) -> list[dict]:
        """Retrieve sections from a CV document based on common section headers.
        Args:
            document (Document): The document pydantic model
        Return:
            list[dict]: A list of sections with their content and line numbers.
        """
        self.document = document
        sections = []
        section_id = 0

        section = {"section": "Introduction",
                   "content": [],
                   "lines": [],
                   "id": section_id}
        
        content_buffer = []
        lines_buffer = []

        for i, line in enumerate(self.document.normalized_text.split("\n")):
            if line.strip() == "":
                continue

            if line.strip().lower() in [x.lower() for x in CV_SECTION_HEADERS]:
                
                if content_buffer or lines_buffer:
                    section["content"] = content_buffer
                    section["lines"] = lines_buffer
                    section["id"] = section_id
                    sections.append(section)
                    lines_buffer = []
                    content_buffer = []
                    section_id += 1
                
                    #new section
                    section = {"section": line.strip(),
                                "content": [],
                                "lines": [],
                                "id": section_id}
                
            else:
                content_buffer.append(line.strip())
                lines_buffer.append(i)
        
        #last section
        if content_buffer or lines_buffer:
            section["content"] = content_buffer
            section["lines"] = lines_buffer
            section["id"] = section_id
            sections.append(section)
            
        return sections
    
    def chunk_sections(self, sections: list[dict]) -> list[CVChunk]:
        """Chunk sections into smaller items based on bullet points and headings.
        Args:
            sections (list[dict]): A list of sections with their content and line numbers.
        Return:
            list[CVChunk]: A list of CVChunk models representing the chunks.
        """
        chunk_id = 0
        chunks = []
        in_bullet_continuation = False
        
        for section in sections:
            for i, line in enumerate(section["content"]):

                #bullet points (check first)
                if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                    chunks.append(CVChunk(section_id=section["id"],
                                  text=line.strip(),
                                  section=section["section"],
                                  chunk_type="ITEM",
                                  chunk_id=chunk_id,
                                  location=section["lines"][i]))
                    chunk_id += 1
                    in_bullet_continuation = True
                    continue
                
                # Continuation of previous bullet point (starts with lowercase or is all caps)
                if in_bullet_continuation and line[0].islower() and (line.endswith(".") or len(line)>100):
                    chunks[-1].text += " " + line.strip()
                    continue

                #headings (only if not in bullet continuation)
                if not in_bullet_continuation and len(line.split()) < 15:
                    chunks.append(CVChunk(section_id=section["id"],
                                  text=line.strip(),
                                  section=section["section"],
                                  chunk_type="HEADING",
                                  chunk_id=chunk_id,
                                  location=section["lines"][i]))
                    chunk_id += 1
                    in_bullet_continuation = False
                    continue
                
                #other lines
                if ":" in line and len(line.split()) < 15:
                    chunks.append(CVChunk(section_id=section["id"],
                                  text=line.strip(),
                                  section=section["section"],
                                  chunk_type="ITEM",
                                  chunk_id=chunk_id,
                                  location=section["lines"][i]))
                    chunk_id += 1
                    continue

                if len(line.split()) < 10:
                    chunks.append(CVChunk(section_id=section["id"],
                                  text=line.strip(),
                                  section=section["section"],
                                  chunk_type="HEADING",
                                  chunk_id=chunk_id,
                                  location=section["lines"][i]))
                    chunk_id += 1
                    continue
        
        self.chunks = chunks
        return chunks
    
    def save_chunks(self, output_dir: Path | None = None):
        """Save chunks to JSON file.
        
        Args:
            output_dir: Optional custom output directory. Defaults to config.processed_data_dir/CVs
        """
        if not self.chunks:
            print("No chunks to save")
            return
        
        if not self.document:
            print("No document loaded")
            return

        if output_dir is None:
            output_dir = config.processed_data_dir / "CVs"
        
        Path.mkdir(output_dir, parents=True, exist_ok=True)
        
        # Get filename from document source
        source_filename = self.document.filename
        output_file = output_dir / f"{source_filename}_chunks.json"
        
        chunks_data = [chunk.model_dump() for chunk in self.chunks]
        
        with open(output_file, 'w') as f:
            json.dump(chunks_data, f, indent=2)
        
        print(f"Saved {len(self.chunks)} chunks to {output_file}")

    def select_chunks_for_embedding(self, chunk_types: List[str] = None) -> List[CVChunk]:
        """Select CV chunks for embedding based on chunk_type.
        
        Args:
            chunk_types: List of chunk types to include. Defaults to ["ITEM"]
        
        Returns:
            List of selected chunks
        """
        if not self.chunks:
            return []
        
        if chunk_types is None:
            chunk_types = ["ITEM"]
        
        selected = [chunk for chunk in self.chunks if chunk.chunk_type in chunk_types]
        
        print(f"Selected {len(selected)} chunks (types: {chunk_types}) out of {len(self.chunks)} total")
        return  selected

    def process_cv(self, document: Document, save: bool = True) -> List[CVChunk]:
        """Complete pipeline: retrieve sections, chunk, and optionally save.
        
        Args:
            document: CV document to process
            save: Whether to save chunks to file
            
        Returns:
            List of CV chunks
        """
        sections = self._retrieve_sections(document)
        chunks = self.chunk_sections(sections)
        
        if save:
            self.save_chunks()
        
        return chunks

    def reset(self):
        """Reset state for processing a new CV."""
        self.chunks = []
        self.document = None


