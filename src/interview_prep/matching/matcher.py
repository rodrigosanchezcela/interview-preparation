"""file containing implementation for Matcher class."""

from pathlib import Path
import json
import numpy as np
from config import config


class Matcher:
    """Matcher class."""
    
    def __init__(self):
        pass

    def match(self, cv_embeddings: np.ndarray, job_embeddings: np.ndarray) -> list[dict]:
        """Calculate metrics between CV and job description embeddings.
        Args:
            cv_embeddings: Numpy array of CV chunk embeddings
            job_embeddings: Numpy array of job description chunk embeddings
        Returns:
            List of dictionaries containing similarity scores and matched chunks
        """
        #cosine similarity -> regardless of magnitude, captures semantically related entities
        normalized_cv_embeddings = cv_embeddings / np.linalg.norm(cv_embeddings, axis=1, keepdims=True) #(cv_chunks, embedding_dim) / (cv_chunks, 1) -> (cv_chunks, embedding_dim)
        normalized_job_embeddings = job_embeddings / np.linalg.norm(job_embeddings, axis=1, keepdims=True) #(job_chunks, embedding_dim) / (job_chunks, 1) -> (job_chunks, embedding_dim)
        cosine_similarities = np.dot(normalized_cv_embeddings, normalized_job_embeddings.T) #(cv_chunks, job_chunks)

        print("cosine similarities: ")
        print(cosine_similarities)
        return cosine_similarities




