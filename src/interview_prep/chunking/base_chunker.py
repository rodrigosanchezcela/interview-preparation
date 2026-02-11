"""Base class for document chunking strategies."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import json
from config import config
from interview_prep.schemas.cv_schema import CVChunk, CVChunk, Document, JobDescriptionChunk


class BaseChunker(ABC):
    """Abstract base class for document chunking.
    
    Provides common utilities and defines the interface.
    Subclasses must implement their own section parsing and chunking logic.
    """
    
    def __init__(self):
        self.document: Document | None = None
        self.sections : List[Dict[str, Any]] = []
        self.chunks : List[CVChunk | JobDescriptionChunk] = []
        self.text_for_embeddings = []
    
    @abstractmethod
    def parse_sections(self, document):
        """Parse document into coarse sections.
        
        Different for CVs vs Jobs - must be implemented by subclasses.
        
        Args:
            document: Document object with normalized_text
            
        Returns:
            List of section dictionaries with structure appropriate for document type
        """
        pass
    
    @abstractmethod
    def chunk_sections(self, sections: List[Dict[str, Any]]):
        """Convert sections into fine-grained chunks.
        
        Args:
            sections: List of section dictionaries from parse_sections()
            
        Returns:
            List of chunk objects (CVChunk, JobDescriptionChunk, etc.)
        """
        pass

    def clean_chunks_for_embeddings(self) -> List[Any]:
        """Clean chunk text for embedding generation.
        
        This can include removing extra whitespace, normalizing characters, etc.
        Subclasses can override if they have specific cleaning needs.
        
        Args:
            chunks: List of chunk objects
            
        Returns:
            List of cleaned chunk objects
        """
        # Default implementation - just strip whitespace
        for chunk in self.chunks:
            #clean chunk
            clean_text = chunk.text.strip()
            #append clean text
            self.text_for_embeddings.append(clean_text)
        
        self.text_for_embeddings
    
    def process(self, document, save: bool = False) -> List[Any]:
        """Template method: full processing pipeline.
        
        Args:
            document: Document to process
            save: Whether to save chunks to file
            
        Returns:
            List of chunks
        """
        self.document = document
        self.sections = self.parse_sections(document)
        self.chunks = self.chunk_sections(self.sections)
        
        if save:
            self.save_chunks()
        
        return self.chunks
    
    def save_chunks(self, output_dir: Path = None):
        """Save chunks to JSON file.
        
        Args:
            output_dir: Optional custom output directory
        """
        if not self.chunks:
            print("No chunks to save")
            return
        
        if not self.document:
            print("No document loaded")
            return
        
        # Subclasses can override output_dir logic
        if output_dir is None:
            output_dir = self._get_default_output_dir()
        
        Path.mkdir(output_dir, parents=True, exist_ok=True)
        
        source_filename = Path(self.document.source).stem
        output_file = output_dir / f"{source_filename}_chunks.json"
        
        chunks_data = [chunk.model_dump() for chunk in self.chunks]
        
        with open(output_file, 'w') as f:
            json.dump(chunks_data, f, indent=2)
        
        print(f"Saved {len(self.chunks)} chunks to {output_file}")
    
    def _get_default_output_dir(self) -> Path:
        """Get default output directory. Subclasses should override."""
        return config.processed_data_dir
    
    def reset(self):
        """Reset state for processing a new document."""
        self.chunks = []
        self.sections = []
        self.document = None
