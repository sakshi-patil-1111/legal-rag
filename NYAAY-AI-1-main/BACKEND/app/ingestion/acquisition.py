import os
import shutil
import urllib.request
import logging
from typing import Optional

logger = logging.getLogger(__name__)

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "raw")

def acquire_document(source_path_or_url: str, document_name: str) -> Optional[str]:
    """
    Acquires a document from a local path or URL and saves it to the raw data directory.
    
    Args:
        source_path_or_url: Local file path or HTTP/HTTPS URL.
        document_name: The name to save the file as (e.g. 'BNS_2023.pdf')
        
    Returns:
        The absolute path to the saved raw document, or None if acquisition failed.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    destination_path = os.path.join(RAW_DATA_DIR, document_name)
    
    try:
        if source_path_or_url.startswith("http://") or source_path_or_url.startswith("https://"):
            logger.info(f"Downloading from URL: {source_path_or_url}")
            # Use basic urllib for generic URLs; can be expanded with requests if custom headers are needed
            req = urllib.request.Request(
                source_path_or_url, 
                headers={'User-Agent': 'Mozilla/5.0'} # Basic anti-bot mitigation
            )
            with urllib.request.urlopen(req) as response, open(destination_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        else:
            logger.info(f"Copying from local path: {source_path_or_url}")
            if not os.path.exists(source_path_or_url):
                logger.error(f"Local file not found: {source_path_or_url}")
                return None
            
            source_abs = os.path.abspath(source_path_or_url)
            dest_abs = os.path.abspath(destination_path)
            if source_abs != dest_abs:
                shutil.copy2(source_path_or_url, destination_path)
            else:
                logger.info(f"Source and destination are the same. Skipping copy.")
            
        logger.info(f"Successfully acquired document: {destination_path}")
        return destination_path
        
    except Exception as e:
        logger.error(f"Failed to acquire document from {source_path_or_url}: {e}")
        return None
