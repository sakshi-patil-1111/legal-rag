import urllib.request
import json

url = "http://localhost:8000/api/auth/sync"
data = json.dumps({"name": "Test User", "role": "citizen"}).encode("utf-8")
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer mock-token",
    "Origin": "http://127.0.0.1:3000"
}

req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode("utf-8"))
        print("Headers:", response.headers)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode("utf-8"))
except Exception as e:
    print("Error:", str(e))
