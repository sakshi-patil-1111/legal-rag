import sys
import os

# fix print encoding
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.ai.orchestrator import rag_orchestrator
from app.knowledge.metadata_utils import get_canonical_source_name

QUERIES = [
    'tenant eviction notice period',
    'police refusing to register FIR',
    'maternity leave entitlement',
    'consumer complaint for defective product',
    'wrongful salary deduction',
    'what are my fundamental rights regarding freedom of speech',
    'property registration process and mutation',
    'divorce by mutual consent cooling off period'
]

print('Running Balance Check...')
results = []
for q in QUERIES:
    print(f'Query: {q}')
    try:
        res = rag_orchestrator.trigger_pipeline(q)
        chunks = res.get('chunks', [])
        sc_count = 0
        statute_count = 0
        other_count = 0
        for c in chunks:
            meta = c.get('metadata', {})
            src = get_canonical_source_name(meta)
            # if 'v.' is in src, it's likely a case. If 'ACT' or 'CODE' in src, it's a statute.
            if ' v. ' in src or meta.get('case_name'):
                sc_count += 1
            elif 'ACT' in src.upper() or 'CODE' in src.upper() or 'SANHITA' in src.upper() or meta.get('type') == 'statute':
                statute_count += 1
            else:
                other_count += 1
        print(f'  SC: {sc_count} | Statutes: {statute_count} | Other: {other_count}')
        results.append({'query': q, 'sc': sc_count, 'statutes': statute_count, 'other': other_count})
    except Exception as e:
        print(f'  Failed: {e}')

print('\nFinal Results:')
for r in results:
    print(f'Q: {r["query"]} -> SC: {r["sc"]}, Stat: {r["statutes"]}, Other: {r["other"]}')
