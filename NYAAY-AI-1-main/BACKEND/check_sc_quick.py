
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.knowledge.vector_store import vector_store
results = vector_store.collection.get(include=['metadatas'])
metas = results['metadatas']
ids = results['ids']

sc_cases = 0
sc_names = set()
for i, meta in zip(ids, metas):
    if i.startswith('SC_') or (meta and meta.get('document_type') == 'case_law'):
        sc_cases += 1
    if meta and 'case_name' in meta:
        sc_names.add(meta['case_name'])

print(f'Found {sc_cases} SC cases chunks')
print(f'Number of unique SC cases: {len(sc_names)}')
print('Sample:', list(sc_names)[:10])

