import argparse
import logging
import sys
import os

# Ensure the app module is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ingestion.acquisition import acquire_document
from app.ingestion.parser import extract_text
from app.ingestion.normalization import normalize_text
from app.ingestion.structure_detector import detect_structure
from app.ingestion.metadata_extractor import extract_metadata
from app.ingestion.validator import validate_document
from app.ingestion.markdown_generator import generate_markdown

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_pipeline(source: str, name: str, domain: str, act_name: str, doc_type: str = "statute"):
    logger.info(f"--- Starting Generic Ingestion Pipeline for {name} ---")
    
    # Phase 1: Acquisition
    logger.info("Phase 1: Acquisition...")
    raw_path = acquire_document(source, name)
    if not raw_path: return
    
    # Phase 2: Parsing (Text Extraction)
    logger.info("Phase 2: Text Extraction...")
    raw_text = extract_text(raw_path)
    if not raw_text: return
    
    # Phase 3: Normalization
    logger.info("Phase 3: Normalization...")
    norm_text = normalize_text(raw_text)
    
    # Phase 4: Structural Detection
    logger.info("Phase 4: Structural Detection...")
    blocks = detect_structure(norm_text, name)
    
    # Phase 5 & 6: Metadata Extraction & Versioning
    logger.info("Phase 5 & 6: Metadata and Versioning...")
    document_data = extract_metadata(blocks, source, name, domain, act_name, doc_type)
    
    # Phase 7: Validation
    logger.info("Phase 7: Validation...")
    validation_report = validate_document(document_data)
    
    if validation_report["status"] == "FAIL":
        logger.error(f"Validation FAILED for {name}. Errors: {validation_report['errors']}")
    else:
        logger.info(f"Validation PASSED for {name}. No critical errors detected.")
        if validation_report["warnings"]:
            logger.warning(f"Validation Warnings: {validation_report['warnings']}")
        
    # Phase 8: Markdown Generation & Manual Approval Staging
    logger.info("Phase 8: Generating Candidate Markdown...")
    md_path, report_path = generate_markdown(document_data, validation_report)
    
    logger.info(f"--- Pipeline Finished ---")
    logger.info(f"Candidate Markdown: {md_path}")
    logger.info(f"Validation Report: {report_path}")
    logger.info("ACTION REQUIRED: Please manually review the candidate markdown.")
    logger.info("If approved, move the .md file to BACKEND/corpus/ and run pipeline_manager.py.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NYAAY AI Generic Corpus Ingestion Pipeline")
    parser.add_argument("--source", required=True, help="URL or local path to raw document")
    parser.add_argument("--name", required=True, help="File name (e.g. BNS_2023.pdf)")
    parser.add_argument("--domain", required=True, help="Legal Domain (e.g. 'Criminal Law')")
    parser.add_argument("--act", required=True, help="Act Name (e.g. 'Bharatiya Nyaya Sanhita')")
    parser.add_argument("--type", default="statute", help="Document type (e.g. 'statute', 'judgment')")
    args = parser.parse_args()
    
    run_pipeline(args.source, args.name, args.domain, args.act, args.type)
