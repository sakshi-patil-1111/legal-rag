import requests
import json

url = "http://127.0.0.1:8000/api/kanoon/query"
payload = {
    "question": "A police officer refuses to register my FIR even though my laptop was stolen. What legal remedies are available? I bought the laptop online.",
    "document_id": None
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    data = response.json()
    print("SUCCESS")
    print(data.get("answer"))
else:
    print(f"FAILED: {response.status_code}")
    print(response.text)
