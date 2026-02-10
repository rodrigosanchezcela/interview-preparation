"""Wrapper class for embeddings."""

from sentence_transformers import SentenceTransformer
from interview_prep.schemas.cv_schema import CVChunk, JobDescriptionChunk
from interview_prep.utils.text_tools import clean_text_for_embedding
from typing import List
from config import config
import numpy as np
from pathlib import Path
import json

class Embedder:
    """Embedder class."""
    
    def __init__(self):
        self.model = SentenceTransformer(config.embeddings_model)
    
    def calculate_embeddings_chunks(self, list_of_chunks : List[CVChunk] | List[JobDescriptionChunk]) -> np.ndarray:
        # Clean text before embedding
        list_of_text = [clean_text_for_embedding(chunk.text) for chunk in list_of_chunks]
        embeddings=self.model.encode(sentences=list_of_text, show_progress_bar=True)

        return embeddings
    
    def save_embeddings(self, embeddings: np.ndarray, list_of_chunks: List[CVChunk] | List[JobDescriptionChunk], source: str):
        """Save embeddings and chunks together in a single JSON file.
        
        Args:
            embeddings: Numpy array of embeddings
            list_of_chunks: List of chunks that were embedded
            source: Source file path (e.g., path to CV or job description file)
        
        Structure:
            data/embeddings/CVs/{filename}_embeddings.json
            data/embeddings/job_descriptions/{filename}_embeddings.json
        """
        if not source:
            raise ValueError("Source must be provided to save embeddings.")
        
        embeddings_dir = config.data_dir / "embeddings"
        filename_stem = Path(source).stem
        
        # Determine subdirectory based on source path
        if "CVs" in Path(source).parts:
            output_dir = embeddings_dir / "CVs"
        elif "job_descriptions" in Path(source).parts:
            output_dir = embeddings_dir / "job_descriptions"
        else:
            raise ValueError("Source path must contain either 'CVs' or 'job_descriptions' directory.")
        
        Path.mkdir(output_dir, parents=True, exist_ok=True)
        
        # Prepare data structure with embeddings and chunks together
        data = {
            "source": source,
            "filename": filename_stem,
            "embeddings": embeddings.tolist(),
            "embedding_shape": list(embeddings.shape),
            "chunks": [chunk.model_dump() for chunk in list_of_chunks],
            "num_chunks": len(list_of_chunks)
        }
        
        # saving embedddings + chunk data
        output_file = output_dir / f"{filename_stem}_embeddings.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)


        


    
    
    
        