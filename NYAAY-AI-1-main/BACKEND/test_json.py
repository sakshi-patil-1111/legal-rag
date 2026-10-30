import json
import re

text = """{
  "executive_summary": "Line 1
Line 2",
  "key2": "value2"
}"""

print("Original parsing:")
try:
    json.loads(text)
    print("success")
except Exception as e:
    print("failed:", e)

# Let's try a regex to fix unescaped newlines in JSON strings.
# A JSON string is surrounded by double quotes. 
# We can find all literal newlines and escape them, but ONLY inside quotes.
def fix_json_newlines(s):
    # This regex matches double-quoted strings, accounting for escaped quotes inside them
    pattern = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
    def repl(m):
        # Replace actual newlines inside the string with \n
        return '"' + m.group(1).replace('\n', '\\n').replace('\r', '\\r') + '"'
    return pattern.sub(repl, s)

fixed = fix_json_newlines(text)
print("\nFixed JSON:")
print(fixed)

try:
    print("\nParsing fixed:")
    obj = json.loads(fixed)
    print("success:", obj)
except Exception as e:
    print("failed:", e)
