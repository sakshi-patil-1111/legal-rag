import re
from typing import Dict, Any

def validate_document(document_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates structural integrity of a parsed document before Markdown generation.
    Returns a Validation Report JSON dict.
    Implements Phase 7 logic.
    """
    blocks = document_data.get("blocks", [])
    doc_meta = document_data.get("document_metadata", {})
    
    report = {
        "document_id": doc_meta.get("document_id", "Unknown"),
        "status": "PASS",
        "errors": [],
        "warnings": [],
        "stats": {
            "total_blocks": len(blocks),
            "parts": set(),
            "chapters": set(),
            "sections": set()
        }
    }
    
    if not blocks:
        report["errors"].append("Document contains no parsed blocks.")
        report["status"] = "FAIL"
        return report
    
    seen_chunk_ids = set()
    section_numbers = []
    
    for block in blocks:
        meta = block.get("metadata", {})
        text = block.get("text", "")
        
        # Track stats
        if meta.get("part"): report["stats"]["parts"].add(meta["part"])
        if meta.get("chapter"): report["stats"]["chapters"].add(meta["chapter"])
        
        # Detect empty chunk
        if not text.strip():
            report["errors"].append(f"Empty chunk found: {meta.get('chunk_id')}")
            
        # Detect duplicate chunk IDs
        chunk_id = meta.get("chunk_id")
        if chunk_id in seen_chunk_ids:
            report["errors"].append(f"Duplicate chunk ID: {chunk_id}")
        seen_chunk_ids.add(chunk_id)
        
        # Parse section numbers to check contiguity later
        sec_match = re.search(r'^(\d+)', meta.get("section", ""))
        if sec_match:
            sec_num = int(sec_match.group(1))
            section_numbers.append((sec_num, chunk_id))
            report["stats"]["sections"].add(sec_num)
            
    # Check section contiguity (warnings, as some acts genuinely repeal/skip sections)
    section_numbers.sort(key=lambda x: x[0])
    for i in range(1, len(section_numbers)):
        prev_num = section_numbers[i-1][0]
        curr_num = section_numbers[i][0]
        # Ignore duplicate sub-chunks under the same section
        if curr_num == prev_num: 
            continue
        # If it jumps by more than 1
        if curr_num > prev_num + 1:
            report["warnings"].append(f"Possible missing section between {prev_num} and {curr_num}")
            
    # Convert sets to lengths for JSON serialization
    report["stats"]["parts"] = len(report["stats"]["parts"])
    report["stats"]["chapters"] = len(report["stats"]["chapters"])
    report["stats"]["sections"] = len(report["stats"]["sections"])
    
    if report["errors"]:
        report["status"] = "FAIL"
        
    return report
