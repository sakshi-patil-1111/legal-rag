import os
import json
from typing import Dict, Any

CANDIDATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "candidates")

def generate_markdown(document_data: Dict[str, Any], validation_report: Dict[str, Any]):
    """
    Implements Phase 8 (Manual Approval Gate).
    Generates Candidate Markdown and the JSON Validation report in the staging directory.
    """
    os.makedirs(CANDIDATES_DIR, exist_ok=True)
    doc_meta = document_data["document_metadata"]
    
    # Generate Markdown with YAML frontmatter
    md_lines = []
    
    # Frontmatter
    md_lines.append("---")
    md_lines.append(f"document_id: {doc_meta.get('document_id', '')}")
    md_lines.append(f"source_name: {doc_meta.get('source_name', '')}")
    md_lines.append(f"legal_domain: {doc_meta.get('legal_domain', '')}")
    md_lines.append(f"act_name: {doc_meta.get('act_name', '')}")
    md_lines.append(f"document_type: {doc_meta.get('document_type', 'statute')}")
    md_lines.append("---\n")
    
    md_lines.append(f"# {doc_meta.get('act_name', '')}\n")
    
    current_part = ""
    current_chapter = ""
    
    for block in document_data.get("blocks", []):
        meta = block.get("metadata", {})
        
        # Only print headers if they changed
        if meta.get("part") and meta["part"] != current_part:
            current_part = meta["part"]
            md_lines.append(f"## {current_part}\n")
            
        if meta.get("chapter") and meta["chapter"] != current_chapter:
            current_chapter = meta["chapter"]
            md_lines.append(f"### {current_chapter}\n")
            
        # The text block contains the section header and text body
        md_lines.append(f"{block.get('text', '')}\n")
        
    md_content = "\n".join(md_lines)
    
    # Save markdown candidate
    md_path = os.path.join(CANDIDATES_DIR, f"{doc_meta['source_name']}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    # Save validation report
    report_path = os.path.join(CANDIDATES_DIR, f"{doc_meta['source_name']}_validation.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(validation_report, f, indent=4)
        
    return md_path, report_path
