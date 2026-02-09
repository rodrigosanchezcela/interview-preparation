from pydantic import BaseModel
from typing import List, Optional

class Document(BaseModel):
    category: str
    raw_text: str
    normalized_text: str
    source: str

class CVChunk(BaseModel):
    section_id: int
    chunk_id: int
    text: str
    section: Optional[str] = "UNKNOWN"
    chunk_type: str
    location: int

class JobDescriptionChunk(BaseModel):
    id: int
    text: str
    section: Optional[str] = "UNKNOWN"
    chunk_type : str

    


