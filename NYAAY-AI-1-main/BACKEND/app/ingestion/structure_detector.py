import re
from typing import List, Dict, Any

def detect_structure(normalized_text: str, document_name: str) -> List[Dict[str, Any]]:
    """
    Parses normalized text into a hierarchical list of blocks.
    Each block is a dictionary representing a section or text chunk, with inherited context.
    Does not modify wording.
    """
    lines = normalized_text.split('\n')
    
    current_part = ""
    current_chapter = ""
    current_section = ""
    
    structured_blocks = []
    current_text_buffer = []
    
    # Common Indian law regexes
    # Matches "PART I", "PART IX", "Part 1"
    part_pattern = re.compile(r'^PART\s+([A-Z0-9]+)(\s+.*)?$', re.IGNORECASE)
    # Matches "CHAPTER I", "CHAPTER IX", "Chapter 1"
    chapter_pattern = re.compile(r'^CHAPTER\s+([A-Z0-9]+)(\s+.*)?$', re.IGNORECASE)
    # Matches "1. ", "1A. ", "123. Title of section"
    section_pattern = re.compile(r'^(\d+[A-Z]*)\.\s+(.*)$')
    
    def flush_buffer():
        if current_text_buffer:
            structured_blocks.append({
                "part": current_part,
                "chapter": current_chapter,
                "section": current_section,
                "text": "\n".join(current_text_buffer).strip()
            })
            current_text_buffer.clear()

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        part_match = part_pattern.match(line_clean)
        chapter_match = chapter_pattern.match(line_clean)
        section_match = section_pattern.match(line_clean)
        
        if part_match:
            flush_buffer()
            current_part = line_clean
            current_chapter = "" # Reset chapter when part changes
            current_section = ""
            
        elif chapter_match:
            flush_buffer()
            current_chapter = line_clean
            current_section = ""
            
        elif section_match:
            flush_buffer()
            current_section = line_clean
            current_text_buffer.append(line_clean) # Keep section title in text
            
        else:
            current_text_buffer.append(line_clean)
            
    # Flush remaining text
    flush_buffer()
        
    return structured_blocks
