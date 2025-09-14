import requests
import json

url = "http://localhost:8080"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {}
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(payload), headers=headers)

print("Status:", response.status_code)
print("Response:", response.text)