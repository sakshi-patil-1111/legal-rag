with open('app/ai/orchestrator.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('gemini-2.5-flash', 'gemini-3.6-flash')

with open('app/ai/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated model to gemini-3.6-flash")
