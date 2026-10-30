import os
import hashlib
from datetime import datetime
import json
import logging
from abc import ABC, abstractmethod
import requests
import time

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PARSED_DIR = os.path.join(DATA_DIR, "parsed")
VALIDATED_DIR = os.path.join(DATA_DIR, "validated")
APPROVED_DIR = os.path.join(DATA_DIR, "approved")

def ensure_directories():
    for directory in [DOWNLOADS_DIR, RAW_DIR, PARSED_DIR, VALIDATED_DIR, APPROVED_DIR]:
        os.makedirs(directory, exist_ok=True)

class AcquisitionProvider(ABC):
    """
    Abstract Base Class for Acquisition Providers.
    Ensures that downloading and parsing are independent of the source.
    """
    @abstractmethod
    def fetch_document(self, act_id: str, source_uri: str) -> tuple[bytes, dict]:
        """
        Fetches the document from the source.
        Returns:
            bytes: The raw document content (HTML, PDF, TXT, etc.)
            dict: The provenance metadata associated with this fetch.
        """
        pass

class GitHubProvider(AcquisitionProvider):
    """
    Downloads raw text/markdown from public GitHub repositories (e.g. CivicTech datasets).
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "NYAAY AI Acquisition Subsystem"})

    def fetch_document(self, act_id: str, source_uri: str) -> tuple[bytes, dict]:
        logger.info(f"Fetching {act_id} via GitHubProvider from {source_uri}")
        response = self.session.get(source_uri)
        response.raise_for_status()
        raw_bytes = response.content
        
        provenance = {
            "source": {
                "authority": "GitHub Open Data",
                "url": source_uri,
                "downloaded_at": datetime.utcnow().isoformat() + "Z",
                "downloaded_by": "system",
                "license": "Public Domain / Open Source",
                "sha256_original": hashlib.sha256(raw_bytes).hexdigest(),
                "sha256_parsed": None
            },
            "document_id": act_id,
            "status": "DOWNLOADED",
            "provider": "GitHubProvider"
        }
        return raw_bytes, provenance

class LocalDirectoryProvider(AcquisitionProvider):
    """
    Reads pre-downloaded files from a local offline archive directory.
    Useful when WAFs block automated downloading, allowing manual batch imports.
    """
    def fetch_document(self, act_id: str, source_uri: str) -> tuple[bytes, dict]:
        logger.info(f"Fetching {act_id} via LocalDirectoryProvider from {source_uri}")
        if not os.path.exists(source_uri):
            raise FileNotFoundError(f"Local file not found: {source_uri}")
            
        with open(source_uri, "rb") as f:
            raw_bytes = f.read()
            
        provenance = {
            "source": {
                "authority": "Manual Import",
                "url": f"file://{source_uri}",
                "downloaded_at": datetime.utcnow().isoformat() + "Z",
                "downloaded_by": "admin",
                "license": "Assumed Public Domain",
                "sha256_original": hashlib.sha256(raw_bytes).hexdigest(),
                "sha256_parsed": None
            },
            "document_id": act_id,
            "status": "DOWNLOADED",
            "provider": "LocalDirectoryProvider"
        }
        return raw_bytes, provenance

class AcquisitionManager:
    """
    Manages the lifecycle of downloading documents using registered providers.
    Saves outputs to the immutable downloads/ directory.
    """
    def __init__(self):
        ensure_directories()
        self.providers = {
            "github": GitHubProvider(),
            "local": LocalDirectoryProvider()
        }

    def download_act(self, provider_name: str, act_id: str, source_uri: str) -> dict:
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
            
        provider = self.providers[provider_name]
        raw_bytes, provenance = provider.fetch_document(act_id, source_uri)
        
        # Determine extension based on URI (fallback to .txt)
        ext = ".txt"
        if source_uri.endswith(".md"): ext = ".md"
        elif source_uri.endswith(".html"): ext = ".html"
        elif source_uri.endswith(".json"): ext = ".json"
        elif source_uri.endswith(".pdf"): ext = ".pdf"
        
        filename = f"{act_id}{ext}"
        save_path = os.path.join(DOWNLOADS_DIR, filename)
        
        with open(save_path, "wb") as f:
            f.write(raw_bytes)
            
        logger.info(f"Saved raw archive to {save_path}")
        
        prov_path = os.path.join(DOWNLOADS_DIR, f"{act_id}_provenance.json")
        with open(prov_path, "w", encoding="utf-8") as f:
            json.dump(provenance, f, indent=4)
            
        return provenance

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    parser = argparse.ArgumentParser(description="Acquisition Manager")
    parser.add_argument("--provider", required=True, choices=["github", "local"], help="The provider to use")
    parser.add_argument("--act_id", required=True, help="Unique identifier for the Act")
    parser.add_argument("--uri", required=True, help="The source URI (URL or file path)")
    
    args = parser.parse_args()
    
    manager = AcquisitionManager()
    manager.download_act(args.provider, args.act_id, args.uri)
