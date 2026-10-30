import os
import json
import hashlib
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")

os.makedirs(DOWNLOADS_DIR, exist_ok=True)

acts = {
    "Constitution_of_India": {
        "text": "# Constitution of India\n\n## PART III - Fundamental Rights\n\n**Article 14. Equality before law.**\nThe State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.\n\n**Article 21. Protection of life and personal liberty.**\nNo person shall be deprived of his life or personal liberty except according to procedure established by law.\n",
        "authority": "Constituent Assembly"
    },
    "Indian_Contract_Act_1872": {
        "text": "# Indian Contract Act, 1872\n\n## CHAPTER I - Of the Communication, Acceptance and Revocation of Proposals\n\n**Section 3. Communication, acceptance and revocation of proposals.**\nThe communication of proposals, the acceptance of proposals, and the revocation of proposals and acceptances, respectively, are deemed to be made by any act or omission of the party proposing, accepting or revoking, by which he intends to communicate such proposal, acceptance or revocation, or which has the effect of communicating it.\n\n**Section 4. Communication when complete.**\nThe communication of a proposal is complete when it comes to the knowledge of the person to whom it is made.\n",
        "authority": "Ministry of Law and Justice"
    },
    "CPC_1908": {
        "text": "# Code of Civil Procedure, 1908\n\n## PART I - Suits in General\n\n**Section 9. Courts to try all civil suits unless barred.**\nThe Courts shall (subject to the provisions herein contained) have jurisdiction to try all suits of a civil nature excepting suits of which their cognizance is either expressly or impliedly barred.\n\n**Section 11. Res Judicata.**\nNo Court shall try any suit or issue in which the matter directly and substantially in issue has been directly and substantially in issue in a former suit between the same parties, or between parties under whom they or any of them claim, litigating under the same title, in a Court competent to try such subsequent suit or the suit in which such issue has been subsequently raised, and has been heard and finally decided by such Court.\n",
        "authority": "Ministry of Law and Justice"
    },
    "Transfer_of_Property_Act_1882": {
        "text": "# Transfer of Property Act, 1882\n\n## CHAPTER II - Of Transfers of Property by Act of Parties\n\n**Section 5. Transfer of property defined.**\nIn the following sections \"transfer of property\" means an act by which a living person conveys property, in present or in future, to one or more other living persons, or to himself and one or more other living persons; and \"to transfer property\" is to perform such act.\n\n**Section 54. Sale defined.**\n\"Sale\" is a transfer of ownership in exchange for a price paid or promised or part-paid and part-promised.\n",
        "authority": "Ministry of Law and Justice"
    },
    "Evidence_Act_1872": {
        "text": "# Indian Evidence Act, 1872\n\n## PART I - Relevancy of Facts\n\n**Section 5. Evidence may be given of facts in issue and relevant facts.**\nEvidence may be given in any suit or proceeding of the existence or non-existence of every fact in issue and of such other facts as are hereinafter declared to be relevant, and of no others.\n\n**Section 6. Relevancy of facts forming part of same transaction.**\nFacts which, though not in issue, are so connected with a fact in issue as to form part of the same transaction, are relevant, whether they occurred at the same time and place or at different times and places.\n",
        "authority": "Ministry of Law and Justice"
    }
}

for act_id, act_info in acts.items():
    text = act_info["text"]
    text_bytes = text.encode("utf-8")
    
    # Save markdown
    md_path = os.path.join(DOWNLOADS_DIR, f"{act_id}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(text)
        
    # Save provenance
    provenance = {
        "source": {
            "authority": act_info["authority"],
            "url": "file://mock",
            "downloaded_at": datetime.utcnow().isoformat() + "Z",
            "downloaded_by": "admin",
            "license": "Public Domain",
            "sha256_original": hashlib.sha256(text_bytes).hexdigest(),
            "sha256_parsed": None
        },
        "document_id": act_id,
        "status": "DOWNLOADED",
        "provider": "LocalDirectoryProvider"
    }
    
    prov_path = os.path.join(DOWNLOADS_DIR, f"{act_id}_provenance.json")
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=4)
        
    print(f"Generated mock download for {act_id}")
