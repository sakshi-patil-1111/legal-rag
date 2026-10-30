import os
import json
import logging
from typing import Optional
from .downloader import AcquisitionManager, DOWNLOADS_DIR
from .parser import StatutoryParser
from .validator import StatutoryValidator
from .metadata import MetadataExtractor

logger = logging.getLogger(__name__)

class AmendmentPipeline:
    """
    Checks for updates to existing documents and routes them through the parsing, 
    validating, and metadata extraction pipeline if changes are detected.
    """
    def __init__(self):
        self.manager = AcquisitionManager()
        self.parser = StatutoryParser()
        self.validator = StatutoryValidator()
        self.metadata = MetadataExtractor()
        
    def get_existing_hash(self, act_id: str) -> Optional[str]:
        prov_path = os.path.join(DOWNLOADS_DIR, f"{act_id}_provenance.json")
        if not os.path.exists(prov_path):
            return None
        with open(prov_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("source", {}).get("sha256_original")
            
    def check_and_update(self, provider_name: str, act_id: str, source_uri: str) -> bool:
        """
        Returns True if the document was updated or newly created, False if unchanged.
        """
        existing_hash = self.get_existing_hash(act_id)
        
        # Download again (will overwrite the old download if it exists)
        logger.info(f"Checking for updates on {act_id}...")
        provenance = self.manager.download_act(provider_name, act_id, source_uri)
        
        new_hash = provenance.get("source", {}).get("sha256_original")
        
        if existing_hash == new_hash:
            logger.info(f"No changes detected for {act_id}. Skipping pipeline.")
            return False
            
        logger.info(f"Changes detected for {act_id} (or new file). Routing through pipeline.")
        
        # Execute the pipeline
        filename = None
        for ext in [".md", ".html", ".json", ".pdf", ".txt"]:
            if os.path.exists(os.path.join(DOWNLOADS_DIR, f"{act_id}{ext}")):
                filename = f"{act_id}{ext}"
                break
                
        if not filename:
            logger.error("Could not locate downloaded file.")
            return False
            
        self.parser.process_file(filename)
        self.validator.process_file(f"{act_id}_parsed.json")
        self.metadata.process_file(act_id)
        
        return True

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--act_id", required=True)
    parser.add_argument("--uri", required=True)
    
    args = parser.parse_args()
    
    pipeline = AmendmentPipeline()
    updated = pipeline.check_and_update(args.provider, args.act_id, args.uri)
    print(f"Update applied: {updated}")
