"""Configuration management for the application."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration."""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.data_dir = self.root_dir / "data"
        self.processed_data_dir = self.data_dir / "processed"

        #embeddings
        self.embeddings_model = 'sentence-transformers/all-MiniLM-L6-v2'


config = Config() 
