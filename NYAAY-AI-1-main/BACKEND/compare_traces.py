
import json
with open('BACKEND/baseline_trace.json') as f:
    b = json.load(f)
with open('BACKEND/after_trace.json') as f:
    a = json.load(f)

for k in b.keys():
    print('==============================')
    print(k)
    print('BEFORE SC Queries:', b[k].get('sc_query_used'))
    print('BEFORE SC Cites (', len(b[k].get('final_context_sc_names', [])), '):')
    for n in list(set(b[k].get('final_context_sc_names', []))): print('  - ', n)
    print('-')
    print('AFTER SC Queries:', a[k].get('sc_query_used'))
    print('AFTER SC Cites (', len(a[k].get('final_context_sc_names', [])), '):')
    for n in list(set(a[k].get('final_context_sc_names', []))): print('  - ', n)

