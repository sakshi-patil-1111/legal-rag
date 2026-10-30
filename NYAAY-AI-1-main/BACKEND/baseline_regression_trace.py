
import os, sys, json, time
sys.path.insert(0, os.path.abspath('BACKEND'))
from app.ai.orchestrator import rag_orchestrator
from app.knowledge.hybrid_retriever import hybrid_retriever

# We will monkey-patch hybrid_retriever to capture its inputs and outputs
orig_search_sc_only = hybrid_retriever.search_sc_only
orig_search = hybrid_retriever.search

capture_data = {}

def patched_search_sc_only(query, query_embedding, n_results=10):
    capture_data['sc_query'] = query
    res = orig_search_sc_only(query, query_embedding, n_results)
    capture_data['sc_candidates'] = []
    for rank, r in enumerate(res):
        capture_data['sc_candidates'].append({
            'rank': rank + 1,
            'source_name': r['metadata'].get('source_name', 'Unknown'),
            'case_name': r['metadata'].get('case_name', 'Unknown'),
            'domain': r['metadata'].get('legal_domain', 'Unknown'),
            'score': r['metadata'].get('reranker_score', r['metadata'].get('rrf_score', 0))
        })
    return res

hybrid_retriever.search_sc_only = patched_search_sc_only

QUERIES = {
    'HOMEBUYER': 'Developer delayed possession by 4 years, refuses to refund money or pay interest. Force majeure clause being misused. RERA provisions and Supreme Court precedent.',
    'ADVERSE_POSSESSION': 'What is the limitation period for adverse possession? Does permissive possession turn into hostile possession? Include Supreme Court precedent.',
    'RAPE_CONSENT': 'What are the statutory presumptions regarding consent and absence of physical resistance in rape cases? What Supreme Court judgments establish the applicable principles?',
    'ILLEGAL_ARREST': 'Can a person be detained for more than 24 hours without being produced before a Magistrate? What are the grounds of arrest under CrPC/BNSS? Give Supreme Court judgments.',
    'NATURAL_JUSTICE': 'natural justice audi alteram partem disciplinary dismissal fair hearing adverse administrative action. what Supreme Court judgments govern these principles?'
}

results = {}

for q_name, q_text in QUERIES.items():
    print(f'Running {q_name}...')
    capture_data.clear()
    
    # Run the pipeline
    try:
        final_response = rag_orchestrator.trigger_pipeline(question=q_text)
    except Exception as e:
        final_response = {'error': str(e)}
        
    cites = final_response.get('citations', [])
    sc_cites = [c for c in cites if 'Supreme Court' in c.get('source_name', '') or c.get('metadata', {}).get('court_level') == 'Supreme Court' or c.get('metadata', {}).get('document_type') == 'case_law']
    
    results[q_name] = {
        'query': q_text,
        'sc_query_used': capture_data.get('sc_query'),
        'sc_candidates_ranked': capture_data.get('sc_candidates', []),
        'final_context_total': len(cites),
        'final_context_sc': len(sc_cites),
        'final_context_sc_names': [c.get('source_name') for c in sc_cites],
        'answer': final_response.get('answer', '')
    }

with open('BACKEND/baseline_trace.json', 'w') as f:
    json.dump(results, f, indent=2)
print('Done. Saved to baseline_trace.json')

