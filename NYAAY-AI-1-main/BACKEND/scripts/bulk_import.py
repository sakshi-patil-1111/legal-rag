import os
import logging
from typing import Dict, Any

import sys

# Ensure Python path includes the backend directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.acquisition.update_checker import AmendmentPipeline

logger = logging.getLogger(__name__)

def run_bulk_import(import_dir: str):
    """
    Processes a directory of raw acts using the LocalDirectoryProvider.
    Generates a batch report.
    """
    logger.info(f"Starting bulk import from {import_dir}")
    
    if not os.path.exists(import_dir):
        logger.error(f"Import directory {import_dir} does not exist.")
        return
        
    pipeline = AmendmentPipeline()
    stats = {
        "acts_processed": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0
    }
    
    for filename in os.listdir(import_dir):
        if not (filename.endswith(".md") or filename.endswith(".txt") or filename.endswith(".html")):
            continue
            
        act_id = os.path.splitext(filename)[0]
        file_path = os.path.join(import_dir, filename)
        
        try:
            logger.info(f"Processing {act_id}...")
            updated = pipeline.check_and_update(
                provider_name="local",
                act_id=act_id,
                source_uri=file_path
            )
            
            stats["acts_processed"] += 1
            if updated:
                stats["updated"] += 1
            else:
                stats["skipped"] += 1
                
        except Exception as e:
            logger.error(f"Failed to process {act_id}: {e}")
            stats["failed"] += 1
            
    logger.info(f"Bulk import complete: {stats}")
    return stats

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--import_dir", required=True, help="Directory containing raw acts to import")
    args = parser.parse_args()
    
    run_bulk_import(args.import_dir)
