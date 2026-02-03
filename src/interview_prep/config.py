"""Configuration management for the application."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration."""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.root_dir / "data"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


config = Config()
