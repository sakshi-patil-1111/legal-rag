# NYAAY AI - Generic Ingestion Pipeline

## Overview
This generic pipeline replaces the manual scraping of Acts. It is designed to download an authentic legal PDF/TXT file, parse it structurally, validate the numbering, and output a Candidate Markdown file for human review before it is committed to the main `BACKEND/corpus/` vector database.

## Workflow

### 1. Run the Pipeline
Use the `pipeline.py` script to fetch and process a raw document.

```bash
python app/ingestion/pipeline.py \
    --source "https://example.com/bns.pdf" \
    --name "BNS_2023.pdf" \
    --domain "Criminal Law" \
    --act "Bharatiya Nyaya Sanhita"
```
You can also use a local file path for `--source`.

### 2. Manual Review
The pipeline will NOT automatically add the document to the corpus or embed it. Instead, it places a markdown candidate and a JSON validation report in:
`BACKEND/data/candidates/`

1. Review the `_validation.json` file.
   - If `"status": "FAIL"`, fix the PDF or tweak the structural regexes in `app/ingestion/structure_detector.py` to handle the specific layout anomalies.
   - If `"status": "PASS"`, proceed to human review.
2. Open the generated `.md` file to verify the formatting looks legally authentic and hasn't dropped headers or mixed up columns.

### 3. Approve and Embed
Once you (the human reviewer) are satisfied, move the `.md` file into the active corpus folder:
```bash
# On Windows PowerShell
Move-Item data\candidates\BNS_2023.md corpus\
```

Then, run the embedding pipeline to push it into ChromaDB and the BM25 index:
```bash
python scripts/pipeline_manager.py build
```

This staging architecture guarantees zero hallucination, structural accuracy, and complete human-in-the-loop auditability.
