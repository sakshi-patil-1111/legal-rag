import os
import sys
import json
import shutil
import logging
import argparse

# Ensure Python path includes the backend directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingestion.pipeline import run_pipeline
from scripts.pipeline_manager import build_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CANDIDATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "candidates")
CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")

def process_single(source: str, name: str, domain: str, act: str, doc_type: str):
    logger.info(f"Orchestrating single ingestion for {name}...")
    # 1. Parse -> MD
    run_pipeline(source, name, domain, act, doc_type)
    
    # 2. Move to Corpus
    source_name = name.upper().replace(".PDF", "").replace(".TXT", "").replace(".MD", "")
    cand_path = os.path.join(CANDIDATES_DIR, f"{source_name}.md")
    dest_path = os.path.join(CORPUS_DIR, f"{source_name}.md")
    
    if os.path.exists(cand_path):
        os.makedirs(CORPUS_DIR, exist_ok=True)
        shutil.move(cand_path, dest_path)
        logger.info(f"Moved {cand_path} to {dest_path}")
    else:
        logger.error(f"Failed to generate candidate MD for {name}")
        return
        
    # 3. Index
    build_pipeline()

def process_batch(batch_dir: str):
    logger.info(f"Orchestrating batch ingestion from {batch_dir}...")
    manifest_path = os.path.join(batch_dir, "manifest.json")
    
    if not os.path.exists(manifest_path):
        logger.error(f"manifest.json not found in {batch_dir}")
        return
        
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    for item in manifest:
        source = os.path.join(batch_dir, item["file"])
        name = item["file"]
        domain = item.get("domain")
        act = item.get("act_name")
        doc_type = item.get("type", "statute")
        
        if not all([domain, act]):
            logger.error(f"Missing mandatory metadata in manifest for {name}")
            continue
            
        logger.info(f"Processing {name} from batch...")
        run_pipeline(source, name, domain, act, doc_type)
        
        source_name = name.upper().replace(".PDF", "").replace(".TXT", "").replace(".MD", "")
        cand_path = os.path.join(CANDIDATES_DIR, f"{source_name}.md")
        dest_path = os.path.join(CORPUS_DIR, f"{source_name}.md")
        
        if os.path.exists(cand_path):
            os.makedirs(CORPUS_DIR, exist_ok=True)
            shutil.move(cand_path, dest_path)
            logger.info(f"Moved {cand_path} to {dest_path}")
        else:
            logger.error(f"Failed to generate candidate MD for {name}")
            
    # Run bulk indexing and BM25 rebuild once at the end
    logger.info("Batch parsing complete. Triggering index build...")
    build_pipeline()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NYAAY AI End-to-End Ingestion Orchestrator")
    parser.add_argument("--mode", choices=["single", "batch"], required=True, help="Ingestion mode")
    parser.add_argument("--batch_dir", help="Directory containing raw files and manifest.json (batch mode)")
    parser.add_argument("--source", help="Path or URL to raw file (single mode)")
    parser.add_argument("--name", help="Filename (single mode)")
    parser.add_argument("--domain", help="Legal Domain (single mode)")
    parser.add_argument("--act", help="Act Name (single mode)")
    parser.add_argument("--type", default="statute", help="Document type (single mode)")
    
    args = parser.parse_args()
    
    if args.mode == "single":
        if not all([args.source, args.name, args.domain, args.act]):
            logger.error("--source, --name, --domain, and --act are required for single mode")
            sys.exit(1)
        process_single(args.source, args.name, args.domain, args.act, args.type)
    elif args.mode == "batch":
        if not args.batch_dir:
            logger.error("--batch_dir is required for batch mode")
            sys.exit(1)
        process_batch(args.batch_dir)
