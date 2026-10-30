import asyncio
from app.ai.orchestrator import rag_orchestrator
from app.core.config import settings

# Wait for db to be ready maybe?
question = "A police officer refuses to register my FIR even though my laptop was stolen. What legal remedies are available? I bought the laptop online."
response = rag_orchestrator.trigger_pipeline(question, task_type="QA")

print("=== ANSWER ===")
print(response["answer"])
print("=== CITATIONS ===")
for c in response["citations"]:
    print(c["marker"], c["source_name"], "Used:", c["chunk_used_by_llm"])
print("=== METRICS ===")
print(response["metrics"])
