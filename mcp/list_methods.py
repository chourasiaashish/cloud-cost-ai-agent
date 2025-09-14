import requests
import json

url = "http://localhost:8080/"

def rpc_call(method, params=None, id=1):
    payload = {
        "jsonrpc": "2.0",
        "id": id,
        "method": method,
        "params": params or {}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()

# 1. Initialize
init_resp = rpc_call("initialize")
print("✅ Initialize response:", json.dumps(init_resp, indent=2))

# 2. List available methods
methods_resp = rpc_call("methods")
print("\n✅ Available methods:", json.dumps(methods_resp, indent=2))