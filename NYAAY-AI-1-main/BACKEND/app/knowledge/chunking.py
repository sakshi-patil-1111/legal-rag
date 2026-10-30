import re
from typing import List, Dict, Any
import uuid

class LegalStructuralChunker:
    def __init__(self, max_chunk_size: int = 1500, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        # Regex patterns to detect structural boundaries
        self.patterns = {
            "part": r"^(?:PART|Part)\s+([IVXLCDM\d]+)",
            "chapter": r"^(?:CHAPTER|Chapter)\s+([IVXLCDM\d]+)",
            "section": r"^(?:SECTION|Section)\s+(\d+[A-Z]?)",
            "article": r"^(?:ARTICLE|Article)\s+(\d+[A-Z]?)",
        }

    def chunk_text(self, text: str, base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits text structurally based on legal hierarchy (Act -> Chapter -> Section/Article).
        Ensures headings are preserved and metadata is correctly enriched.
        """
        paragraphs = text.split('\n')
        chunks = []
        
        current_chunk = ""
        current_context = {
            "Part": None,
            "Chapter": None,
            "Section": None,
            "Article": None,
            "Heading": None
        }
        
        # A buffer to hold lines for the current chunk
        lines_buffer = []
        char_count = 0
        
        for p in paragraphs:
            para = p.strip()
            if not para:
                continue
                
            # Check for structural changes without mutating context yet
            pending = None  # (ContextKey, value, is_section_or_article, heading_line)
            for key, pattern in self.patterns.items():
                match = re.match(pattern, para)
                if match:
                    pending = (key.capitalize(), match.group(1), key in ("section", "article"), para)
                    break
                    
            # Flush the buffer under the CURRENT (old) context on a boundary
            if pending and lines_buffer:
                is_section_boundary = pending[2]
                if is_section_boundary or char_count > 200:
                    chunks.append(self._create_chunk(lines_buffer, current_context, base_metadata))
                    lines_buffer = []
                    char_count = 0
                    
            # Now apply the update for the NEW section and reset lower hierarchy levels
            if pending:
                ctx_key, ctx_val, is_heading, heading_line = pending
                current_context[ctx_key] = ctx_val
                if ctx_key == "Part":
                    current_context["Chapter"] = None
                    current_context["Section"] = None
                    current_context["Article"] = None
                    current_context["Heading"] = None
                elif ctx_key == "Chapter":
                    current_context["Section"] = None
                    current_context["Article"] = None
                    current_context["Heading"] = None
                if is_heading:
                    current_context["Heading"] = heading_line
                    
            # If line is short and uppercase, it might be a sub-heading, append it
            lines_buffer.append(para)
            char_count += len(para) + 1
            
            # If we exceed max size, flush
            if char_count >= self.max_chunk_size:
                chunks.append(self._create_chunk(lines_buffer, current_context, base_metadata))
                # Keep overlap (last 1-2 paragraphs depending on length)
                overlap_lines = lines_buffer[-2:] if len(lines_buffer) > 2 else lines_buffer[-1:]
                lines_buffer = []
                char_count = 0
                
                # Prepend overlap and context heading if relevant
                if current_context["Heading"]:
                    lines_buffer.append(f"[{current_context['Heading']} - continued]")
                    char_count += len(lines_buffer[0]) + 1
                    
                for ol in overlap_lines:
                    lines_buffer.append(ol)
                    char_count += len(ol) + 1
                    
        # Flush remainder
        if lines_buffer:
            chunks.append(self._create_chunk(lines_buffer, current_context, base_metadata))
            
        return chunks

    def _create_chunk(self, lines: List[str], context: Dict[str, str], base_metadata: Dict[str, Any]) -> Dict[str, Any]:
        text = "\n".join(lines)
        metadata = base_metadata.copy()
        
        # Enrich metadata with structural context
        if context["Part"]: metadata["part"] = context["Part"]
        if context["Chapter"]: metadata["chapter"] = context["Chapter"]
        if context["Section"]: metadata["section"] = context["Section"]
        if context["Article"]: metadata["article"] = context["Article"]
        
        # Build context string for the text itself to help Dense Retrieval
        context_prefix = []
        from app.knowledge.metadata_utils import get_canonical_source_name
        src_name = get_canonical_source_name(metadata)
        if src_name and src_name != "Unknown": context_prefix.append(src_name)
        if context["Chapter"]: context_prefix.append(f"Chapter {context['Chapter']}")
        if context["Section"]: context_prefix.append(f"Section {context['Section']}")
        if context["Article"]: context_prefix.append(f"Article {context['Article']}")
        
        if context_prefix:
            prefix = " > ".join(context_prefix)
            text = f"[{prefix}]\n{text}"
            
        return {
            "id": str(uuid.uuid4()),
            "text": text.strip(),
            "metadata": metadata
        }

semantic_chunker = LegalStructuralChunker()
