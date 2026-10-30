
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.knowledge.vector_store import vector_store
results = vector_store.sc_collection.get(include=['metadatas'])
metas = results['metadatas']
ids = results['ids']

print(f'Found {len(ids)} chunks in supreme_court_cases collection')
sc_names = set(m.get('case_name') for m in metas if m and 'case_name' in m)
print(f'Number of unique SC cases: {len(sc_names)}')
print('Sample:', list(sc_names)[:10])

