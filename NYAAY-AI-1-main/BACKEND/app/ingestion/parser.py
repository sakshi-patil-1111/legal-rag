import logging
from typing import Optional

logger = logging.getLogger(__name__)

def extract_text(file_path: str) -> Optional[str]:
    """
    Extracts raw text from a document (PDF, TXT, MD, HTML).
    
    Args:
        file_path: Absolute path to the raw document.
        
    Returns:
        Raw extracted text as a string, or None if extraction fails.
    """
    try:
        if file_path.lower().endswith(".pdf"):
            import pymupdf
            doc = pymupdf.open(file_path)
            text_content = []
            for page in doc:
                # Extract blocks and sort top-to-bottom, left-to-right
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))
                for b in blocks:
                    if len(b) >= 5:
                        text = b[4].strip()
                        if text:
                            text_content.append(text)
            return "\n\n".join(text_content)
            
        elif file_path.lower().endswith((".txt", ".md")):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
                
        else:
            logger.error(f"Unsupported file type for extraction: {file_path}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to parse document {file_path}: {e}")
        return None
