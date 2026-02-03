"""Interview Preparation Tool - A comprehensive tool for technical interview preparation."""

from interview_prep.__version__ import __version__

__all__ = ["__version__", "main"]


def main() -> None:
    """Entry point for the CLI application."""
    print(f"Interview Prep Tool v{__version__}")
    print("Welcome to your interview preparation assistant!")
    print("\nUse 'interview-prep --help' for more information.")

