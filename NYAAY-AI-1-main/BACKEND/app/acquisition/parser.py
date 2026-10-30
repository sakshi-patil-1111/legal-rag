import os
import json
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")
PARSED_DIR = os.path.join(DATA_DIR, "parsed")

class StatutoryParser:
    """
    Parses raw textual statutory documents into a structured hierarchy.
    Extracts Chapters, Sections, and Subsections.
    """
    def __init__(self):
        os.makedirs(PARSED_DIR, exist_ok=True)
        
    def parse_markdown(self, act_id: str, raw_text: str) -> Dict[str, Any]:
        """
        Parses Markdown-formatted bare acts into a structured dictionary.
        Returns a dictionary containing the hierarchy and the parser confidence score.
        """
        hierarchy = []
        current_chapter = None
        
        # Regex patterns
        chapter_pattern = re.compile(r"^##\s+(?:CHAPTER|PART)\s+([A-ZIVX]+)\s+-\s+(.+)$", re.MULTILINE)
        section_pattern = re.compile(r"^\*\*(?:Section|Article|Clause)?\s*(\d+[A-Z]?)\.\s+(.+?)\.\*\*", re.MULTILINE)
        
        lines = raw_text.split("\n")
        
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            ch_match = chapter_pattern.match(line)
            if ch_match:
                if current_section:
                    current_section["text"] = "\n".join(current_text)
                    hierarchy.append(current_section)
                    current_section = None
                    current_text = []
                current_chapter = {"number": ch_match.group(1), "title": ch_match.group(2)}
                continue
                
            sec_match = section_pattern.match(line)
            if sec_match:
                if current_section:
                    current_section["text"] = "\n".join(current_text)
                    hierarchy.append(current_section)
                    
                current_section = {
                    "chapter": current_chapter["number"] if current_chapter else None,
                    "chapter_title": current_chapter["title"] if current_chapter else None,
                    "section_number": sec_match.group(1),
                    "section_title": sec_match.group(2),
                    "text": ""
                }
                current_text = []
                continue
                
            if current_section:
                current_text.append(line)
                
        if current_section:
            current_section["text"] = "\n".join(current_text)
            hierarchy.append(current_section)
            
        # Confidence logic (simple heuristic for now)
        confidence = "HIGH" if len(hierarchy) > 0 else "LOW"
        
        return {
            "act_id": act_id,
            "sections": hierarchy,
            "parser_report": {
                "hierarchy_score": 100 if confidence == "HIGH" else 0,
                "missing_sections": 0, # Validator will calculate this
                "duplicate_sections": 0,
                "broken_references": 0,
                "confidence": confidence
            }
        }

    def process_file(self, filename: str):
        logger.info(f"Parsing {filename}...")
        act_id = os.path.splitext(filename)[0]
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        parsed_data = self.parse_markdown(act_id, raw_text)
        
        save_path = os.path.join(PARSED_DIR, f"{act_id}_parsed.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=4)
            
        logger.info(f"Successfully parsed {len(parsed_data['sections'])} sections. Saved to {save_path}")
        return parsed_data

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", required=True, help="Filename in downloads/ to parse")
    args = parser.parse_args()
    
    p = StatutoryParser()
    p.process_file(args.filename)
