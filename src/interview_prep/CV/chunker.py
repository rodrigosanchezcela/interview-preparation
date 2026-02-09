
from interview_prep.schemas.cv_schema import Document, CVChunk
from constants import CV_SECTION_HEADERS, TECHNICAL_SKILLS

class CVChunker:
    """Class to chunk CVs into small items."""

    def _retrieve_sections(self, document: Document) -> list[dict]:
        """Retrieve sections from a CV document based on common section headers.
        Args:
            document (Document): The document pydantic model
        Return:
            list[dict]: A list of sections with their content and line numbers.
        """
        sections = []
        section_id = 0

        section = {"section": "Introduction",
                   "content": [],
                   "lines": [],
                   "id": section_id}
        
        content_buffer = []
        lines_buffer = []

        for i, line in enumerate(document.normalized_text.split("\n")):
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

        return chunks