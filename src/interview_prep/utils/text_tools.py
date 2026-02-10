"""Utilities for text processing."""

import re
import unicodedata
from config import config


def expand_contractions(text: str) -> str:
    """Function to expand common English contractions in the text."""
    contractions_dict = {
        "can't": "cannot",
        "won't": "will not",
        "n't": " not",
        "'re": " are",
        "'s": " is",
        "'d": " would",
        "'ll": " will",
        "'t": " not",
        "'ve": " have",
        "'m": " am"
    }
    contractions_re = re.compile('(%s)' % '|'.join(contractions_dict.keys()))

    def replace(match):
        return contractions_dict[match.group(0)]

    return contractions_re.sub(replace, text)

def remove_extra_whitespace(text:str) -> str:
    """Function to remove extra whitespace from text."""
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text

def remove_accents(text: str)->str:
    """Function to remove accents from characters in the text."""
    text = re.sub(r'´', '', text)
    text = re.sub(r'¨', '', text)
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def fix_hyphenation(text: str) -> str:
    """Function to fix hyphenation issues in the text."""
    # Repair hyphenation at line breaks
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"(\w),\n(\w)", r"\1, \2", text)
    return text


def normalize_text(text: str) -> str:
    """Function to normalize text"""

    normalized_text = expand_contractions(text)

    #Hyphenation repair (e.g., "exam-\nple" -> "example")
    normalized_text = fix_hyphenation(normalized_text)

    #Unicode normalization
    normalized_text = remove_accents(normalized_text)

    normalized_text = remove_extra_whitespace(normalized_text)

    #Remove multiple newlines
    normalized_text = re.sub(r'\n{3,}', '\n\n', normalized_text)

    return normalized_text

### chunking util functions
def normalize_chunk_text(text: str) -> str:
    # Safe at chunk-level: collapse whitespace inside a chunk
    return re.sub(r"\s+", " ", text).strip()

def clean_text_for_embedding(text: str) -> str:
    """Clean text specifically for embedding generation.
    
    Removes:
    - Bullet points (•, ◦, ▪, –, ―, -, *)
    - Excessive whitespace
    - Special characters that don't add semantic meaning
    - Leading/trailing punctuation
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text suitable for embedding
    """
    # Remove bullet point markers at the start
    text = re.sub(r'^[\s•◦▪–―\-\*]+', '', text)
    
    # Remove multiple bullet points within text
    text = re.sub(r'[\s•◦▪]+', ' ', text)
    
    # Replace special dashes with regular hyphens
    text = re.sub(r'[–―]', '-', text)
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove trailing incomplete sentences (ends with comma/semicolon/colon but no period)
    # This catches cases like "Awareness of" or "such as"
    if text and text[-1] in ',:;':
        # Try to find the last complete sentence
        sentences = re.split(r'[.!?]\s+', text)
        if len(sentences) > 1:
            text = '. '.join(sentences[:-1]) + '.'
    
    return text

def is_line_header(line: str) -> bool:
    """Determine if a line is a header based on formatting cues."""
    line = line.strip()
    
    # Empty lines are not headers
    if not line:
        return False
    
    if line in config.cv_sections:
        return True
    
def is_heading(line:str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.startswith("•"):
        return False
    if s.endswith("."):  # sentences usually end with period => continuation
        return False

    # Dates / ranges often indicate a heading line
    if re.search(r"\b(19|20)\d{2}\b", s) and any(ch in s for ch in ["-", "–", "—"]):
        return True

    # Location-like "City, Country"
    if "," in s and len(s) <= 40:
        return True

    # Very short lines are often headings (company / institution)
    if len(s) <= 28:
        return True

    # Lots of TitleCase words and no obvious sentence punctuation
    words = [w for w in re.findall(r"[A-Za-zÀ-ÿ]+", s) if w]
    if words:
        titleish = sum(1 for w in words if w[0].isupper())
        if titleish / len(words) >= 0.7 and len(s) <= 55:
            return True

    return False