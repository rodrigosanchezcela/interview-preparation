"""File for chunking CVs into meaningful sections."""
from typing import List, Dict, Any
from interview_prep.schemas.cv_schema import CVChunk
from interview_prep.chunking.base_chunker import BaseChunker
from constants import CV_SECTION_HEADERS
from interview_prep.utils.text_tools import sentence_based_chunking


class CVChunker(BaseChunker):
    """Chunker for CV documents.
    
    Implements parsing and chunking logic specific to CVs.
    """
    
    def parse_sections(self, document):
        """Parse CV into sections like Education, Experience, Skills."""
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
        
        self.sections = sections

    def chunk_sections(self):
        """Convert CV sections into fine-grained CVChunk objects."""
        chunks = []
        chunk_id = 0
        for i, section in enumerate(self.sections):
            section_text = ' '.join(section['content'])
            text_chunks = sentence_based_chunking(section_text, chunk_size=300, overlap=100)
            print(text_chunks)
            for chunk_text in text_chunks:
                chunk_id+=1
                chunk = CVChunk(
                    section_id=i,
                    chunk_id=chunk_id,
                    section=section['section'],
                    text=chunk_text,
                    source_document_id=self.document.source,
                    chunk_type="CV_CHUNK",
                    length=len(chunk_text)
                )
                chunks.append(chunk)

        self.chunks = chunks
