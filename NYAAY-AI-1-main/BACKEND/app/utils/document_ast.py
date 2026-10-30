import uuid
import hashlib
import re
from typing import Dict, Any, List
from app.schemas.layout import ASTNode, BlockType, DocumentAST
from app.schemas.drafting import StructuredDocumentObject
from datetime import datetime

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

SECTION_HEADINGS = {
    "FACTS",
    "LEGAL BASIS",
    "LEGAL GROUNDS",
    "GROUNDS",
    "CAUSE OF ACTION",
    "JURISDICTION",
    "LIMITATION",
    "VALUATION",
    "COURT FEE",
    "RELIEF",
    "RELIEFS",
    "RELIEF SOUGHT",
    "PRAYER",
    "PRAYERS",
    "VERIFICATION",
    "ANNEXURES",
    "LIST OF ANNEXURES",
    "DEFICIENCY IN SERVICE",
    "UNFAIR TRADE PRACTICE",
}

SIGNATURE_PHRASES = (
    "yours faithfully",
    "signed by",
    "advocate for",
    "counsel for",
    "deponent",
    "verified at",
)

def _stable_ref(doc: StructuredDocumentObject, prefix: str) -> str:
    seed = f"{doc.document_type}|{doc.title}|{doc.metadata.created_at}|{doc.metadata.version}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8].upper()
    return f"NYAAY-{prefix}-{digest}"

def _created_date(doc: StructuredDocumentObject) -> str:
    try:
        return datetime.fromisoformat(doc.metadata.created_at).strftime("%d %B %Y")
    except Exception:
        return datetime.utcnow().strftime("%d %B %Y")

def _clean_body_paragraph(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    text = re.sub(r"^\s*\d+[\.)]\s+", "", text)
    return text

def _is_signature_like(text: str) -> bool:
    lowered = text.lower().strip()
    return any(lowered.startswith(phrase) for phrase in SIGNATURE_PHRASES)

def _extract_heading(text: str):
    stripped = text.strip()
    if not stripped:
        return None, ""

    match = re.match(r"^([A-Z][A-Z\s/&-]{2,40})\s*[:\-]\s*(.+)$", stripped)
    if match and match.group(1).strip() in SECTION_HEADINGS:
        return match.group(1).strip(), match.group(2).strip()

    normalized = re.sub(r"[^A-Za-z\s/&-]", "", stripped).strip().upper()
    if normalized in SECTION_HEADINGS and len(stripped.split()) <= 5:
        return normalized, ""

    return None, stripped

def _party_rows(parties: Dict[str, str]) -> Dict[str, str]:
    return {
        role.replace("_", " ").title(): value
        for role, value in parties.items()
        if value and not (value.startswith("[") and value.endswith("]"))
    }

def build_document_ast(doc: StructuredDocumentObject) -> DocumentAST:
    nodes: List[ASTNode] = []
    doc_type = (doc.document_type or "").upper()
    
    # 1. Dispatch Method (For Legal Notice)
    if doc_type == "LEGAL_NOTICE":
        nodes.append(ASTNode(
            id=generate_id("dispatch"),
            type=BlockType.PARAGRAPH,
            content={"text": "BY REGISTERED A.D. / SPEED POST / EMAIL"},
            metadata={"bold": True}
        ))
        
        nodes.append(ASTNode(
            id=generate_id("date"),
            type=BlockType.PARAGRAPH,
            content={"text": f"Date: {datetime.utcnow().strftime('%d-%m-%Y')}"}
        ))
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "16pt"}))

        recipient = doc.parties.get("recipient", doc.parties.get("noticee", "[Recipient Name]"))
        nodes.append(ASTNode(
            id=generate_id("to_label"),
            type=BlockType.PARAGRAPH,
            content={"text": "To,"},
            metadata={"keepWithNext": True}
        ))
        nodes.append(ASTNode(
            id=generate_id("to_address"),
            type=BlockType.PARAGRAPH,
            content={"text": recipient},
            metadata={"keepWithNext": True}
        ))
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "16pt"}))

    # 2. Title / Subject
    if doc.title:
        title_text = "LEGAL NOTICE" if doc_type == "LEGAL_NOTICE" else doc.title.upper()
        nodes.append(ASTNode(
            id=generate_id("title"),
            type=BlockType.TITLE,
            content={"text": title_text}
        ))
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "16pt"}))

    # 3. Parties Block
    party_data = _party_rows(doc.parties)
    if doc_type != "LEGAL_NOTICE" and party_data:
        nodes.append(ASTNode(
            id=generate_id("parties_heading"),
            type=BlockType.HEADING,
            content={"text": "PARTIES"}
        ))
        nodes.append(ASTNode(
            id=generate_id("parties"),
            type=BlockType.PARTIES_TABLE,
            content=party_data
        ))
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "16pt"}))

    # 4. Opening (For Legal Notice)
    if doc_type == "LEGAL_NOTICE":
        sender = doc.parties.get("sender", doc.parties.get("client", "[Sender Name]"))
        subject_text = doc.title if doc.title.lower() != "legal notice" else "Legal notice regarding your default."
        
        nodes.append(ASTNode(
            id=generate_id("subject"),
            type=BlockType.SUBJECT,
            content={"text": f"Subject: {subject_text}"}
        ))
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "16pt"}))
        nodes.append(ASTNode(
            id=generate_id("salutation"),
            type=BlockType.PARAGRAPH,
            content={"text": "Sir / Madam,"},
            metadata={"keepWithNext": True}
        ))
        nodes.append(ASTNode(
            id=generate_id("opening"),
            type=BlockType.PARAGRAPH,
            content={"text": f"Under the instructions of and on behalf of my client, {sender}, I hereby serve upon you the following legal notice:"}
        ))

    # 5. Body Paragraphs
    paragraph_number = 1
    for para in doc.body:
        cleaned = _clean_body_paragraph(para)
        if not cleaned or _is_signature_like(cleaned):
            continue
            
        heading, remainder = _extract_heading(cleaned)
        if heading:
            nodes.append(ASTNode(
                id=generate_id("heading"),
                type=BlockType.HEADING,
                content={"text": heading}
            ))
            if not remainder:
                continue
            cleaned = remainder

        nodes.append(ASTNode(
            id=generate_id("para"),
            type=BlockType.NUMBERED_PARAGRAPH,
            content={"number": paragraph_number, "text": cleaned}
        ))
        paragraph_number += 1

    # 6. Demand Clause (For Legal Notice)
    if doc_type == "LEGAL_NOTICE":
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "16pt"}))
        nodes.append(ASTNode(
            id=generate_id("demand"),
            type=BlockType.PARAGRAPH,
            content={"text": "You are hereby called upon to comply with the above within fifteen (15) days from the receipt of this notice, failing which my client shall be constrained to initiate appropriate legal proceedings before the competent forum, at your risk, costs, and consequences."}
        ))

    # 7. Verification Block
    if doc.verification and doc.verification.text:
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "16pt"}))
        nodes.append(ASTNode(
            id=generate_id("verification"),
            type=BlockType.VERIFICATION_BLOCK,
            content={
                "text": doc.verification.text,
                "place": doc.verification.place if doc.verification.place != "[Place]" else "_____________",
                "date": doc.verification.date if doc.verification.date != "[Date]" else "_____________"
            }
        ))

    # 8. Signature Block
    if doc.signature_blocks:
        nodes.append(ASTNode(id=generate_id("spacer"), type=BlockType.SPACER, content={"height": "32pt"}))
        signatures = []
        seen_roles = set()
        sender_name = doc.parties.get("sender", doc.parties.get("client", "")).lower()
        
        for sig in doc.signature_blocks:
            role = "Advocate for the Notice Sender" if doc_type == "LEGAL_NOTICE" else "Counsel for the Client"
            if sig.lower() == sender_name:
                continue
                
            if role not in seen_roles:
                if "[" in sig and "]" in sig:
                    signatures.append({"role": role})
                else:
                    signatures.append({"name": sig, "role": role})
                seen_roles.add(role)
        
        if not signatures:
            signatures.append({"role": "Advocate for the Notice Sender" if doc_type == "LEGAL_NOTICE" else "Counsel for the Client"})

        nodes.append(ASTNode(
            id=generate_id("signature"),
            type=BlockType.SIGNATURE_BLOCK,
            content={
                "closing": "Yours faithfully," if doc_type == "LEGAL_NOTICE" else None,
                "signatures": signatures
            },
            metadata={"keepWithNext": True}
        ))

    # 9. Annexures List
    if doc.annexures:
        nodes.append(ASTNode(id=generate_id("page_break"), type=BlockType.PAGE_BREAK, content={}))
        nodes.append(ASTNode(
            id=generate_id("annexure_heading"),
            type=BlockType.HEADING,
            content={"text": "LIST OF ANNEXURES", "level": 2}
        ))
        
        # Clean redundant "Annexure A Annexure A" wording
        clean_annexures = []
        for i, ann in enumerate(doc.annexures):
            label = f"Annexure - {chr(65+i)}"
            # Strip out the label if LLM prefixed it
            desc = re.sub(rf"^{label}[\s:\-]*", "", ann, flags=re.IGNORECASE).strip()
            desc = re.sub(rf"^Annexure\s+{chr(65+i)}[\s:\-]*", "", desc, flags=re.IGNORECASE).strip()
            clean_annexures.append({"label": label, "desc": desc})
            
        nodes.append(ASTNode(
            id=generate_id("annexures"),
            type=BlockType.ANNEXURE_LIST,
            content={
                "items": clean_annexures
            }
        ))

    return DocumentAST(nodes=nodes)
