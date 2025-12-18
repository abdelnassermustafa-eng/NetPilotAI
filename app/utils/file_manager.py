"""
File handling utilities for NetPilot AI.

Provides helper functions for:
- Creating directories safely
- Saving configuration files
- Loading text files
- Ensuring consistent file operations
"""

from pathlib import Path

def ensure_directory(path: Path) -> None:
    """
    Create a directory if it does not already exist.
    """
    path.mkdir(parents=True, exist_ok=True)

def save_text_file(file_path: Path, content: str) -> None:
    """
    Save text content to a file.
    """
    ensure_directory(file_path.parent)
    file_path.write_text(content, encoding="utf-8")

def load_text_file(file_path: Path) -> str:
    """
    Load and return the contents of a text file.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return file_path.read_text(encoding="utf-8")
