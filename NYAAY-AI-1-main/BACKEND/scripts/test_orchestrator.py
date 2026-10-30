import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.ai.orchestrator import rag_orchestrator

try:
    res = rag_orchestrator.trigger_pipeline("What is anticipatory bail?")
    print("SUCCESS")
    print(res["metrics"])
    print("Answer length:", len(res["answer"]))
except Exception as e:
    import traceback
    traceback.print_exc()
