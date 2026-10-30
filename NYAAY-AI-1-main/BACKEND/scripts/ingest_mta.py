import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.knowledge.ingestion import ingestion_pipeline
from app.knowledge.bm25_manager import bm25_manager

act_text = """# Model Tenancy Act, 2021

## CHAPTER III : RENT, ENHANCEMENT OF RENT AND SECURITY DEPOSIT

### Section 11: Security Deposit
(1) The security deposit to be paid by the tenant in advance shall—
(a) not exceed two months' rent, in case of residential premises; and
(b) not exceed six months' rent, in case of non-residential premises.

(2) The security deposit shall be refunded to the tenant on the date of taking over vacant possession of the premises from the tenant, after making due deduction of any liability of the tenant.

(3) If the landlord refuses to refund the security deposit, or makes unauthorized deductions for alleged repairs without proof or bills, the tenant may approach the Rent Court or Rent Tribunal for recovery of the deposit along with damages. The landlord cannot unilaterally forfeit the entire deposit without establishing the liability of the tenant.
"""

metadata = {
    "source_name": "Model Tenancy Act, 2021",
    "document_type": "statute",
    "legal_domain": "Tenant & Housing",
    "jurisdiction": "India",
    "section": "Section 11",
    "authority": "Parliament of India"
}

def run_ingestion():
    print("Ingesting Model Tenancy Act, 2021...")
    ingestion_pipeline.process_document(
        text=act_text,
        base_metadata=metadata
    )
    
    print("Rebuilding BM25 index...")
    bm25_manager.rebuild_index()
    print("Ingestion complete.")

if __name__ == "__main__":
    run_ingestion()
