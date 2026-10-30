
import sys, os, time, json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.ai.orchestrator import rag_orchestrator
from app.knowledge.vector_store import vector_store

queries = [
    'natural justice audi alteram partem disciplinary dismissal fair hearing Supreme Court',
    'Developer delayed possession by 4 years, refuses to refund money or pay interest. Force majeure clause being misused. Supreme Court precedent.'
]

for q in queries:
    print('Testing Query:', q)
    res = rag_orchestrator.trigger_pipeline(question=q)
    cites = res.get('citations', [])
    sc_cites = [c for c in cites if 'Supreme Court' in c.get('source_name','') or c.get('metadata',{}).get('court_level') == 'Supreme Court' or c.get('metadata',{}).get('document_type') == 'case_law']
    print(f'Total chunks in final context: {len(cites)}')
    print(f'SC chunks in final context: {len(sc_cites)}')
    if sc_cites:
        print('Sample SC chunk:', sc_cites[0].get('source_name'))
    print('-'*50)

