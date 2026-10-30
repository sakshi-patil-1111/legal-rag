import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.ai.orchestrator import rag_orchestrator
print("Testing trigger_pipeline (sync)...")
res = rag_orchestrator.trigger_pipeline("What is rape under BNS?", [])
print("Sync Response Keys:", res.keys())

print("Testing trigger_pipeline_stream (CIVIC)...")
stream = rag_orchestrator.trigger_pipeline_stream("What are my rights if arrested?", [], task_type="CIVIC")
chunks = []
for chunk in stream:
    chunks.append(chunk)
    if "event: result" in chunk:
        try:
            result_json = chunk.replace("event: result\ndata: ", "").strip()
            print("Stream Result Keys:", json.loads(result_json).keys())
        except Exception as e:
            print("Failed to parse result chunk:", chunk)
print("Smoke test complete.")
