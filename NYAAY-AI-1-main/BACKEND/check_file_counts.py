import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.knowledge.vector_store import vector_store

print(f"Total Chunks in DB: {vector_store.collection.count()}")
