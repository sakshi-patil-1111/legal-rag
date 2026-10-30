
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.knowledge.vector_store import vector_store
# Try to find RERA
results = vector_store.collection.get()
metas = results['metadatas']
rera_count = sum(1 for m in metas if m and 'act_name' in m and 'Real Estate' in m['act_name'])
print(f'Found {rera_count} RERA documents by name substring')
acts = set(m.get('act_name') for m in metas if m and 'act_name' in m)
print('Acts containing Real:', [a for a in acts if 'Real' in (a or '')])

