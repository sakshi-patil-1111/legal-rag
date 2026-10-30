import re
import unicodedata

def normalize_text(raw_text: str) -> str:
    """
    Standardizes unicode, whitespace, line endings, and basic formatting
    without modifying the actual legal meaning or words.
    """
    # Unicode normalize to standardize special characters
    text = unicodedata.normalize("NFKC", raw_text)
    
    # Standardize smart quotes to straight quotes
    text = text.replace('"', '"').replace('"', '"').replace("'", "'").replace("'", "'")
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    
    # Strip basic OCR artifacts (like repeating whitespace or form feeds)
    text = re.sub(r'\f', '\n', text)
    
    # Remove common page number footers/headers (e.g., "Page 1 of 50" or just standalone numbers at the edge of blocks)
    text = re.sub(r'(?im)^Page\s+\d+\s+(?:of\s+\d+)?$', '', text)
    text = re.sub(r'(?im)^[\-\—]\s*\d+\s*[\-\—]$', '', text) # e.g. - 12 -
    
    # Clean up excessive line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Ensure spaces after periods if OCR missed them (basic heuristic, careful with abbreviations)
    # text = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', text) # Too risky for legal cross-refs
    
    return text.strip()
