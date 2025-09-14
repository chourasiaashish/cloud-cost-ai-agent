import requests
from azure.identity import DefaultAzureCredential
#pip install azure-identity

# Inputs
subscription_id = "74ebef29-9863-4c57-bd13-b510f4824772"
region = "eastus"
required_vcpu = 2
required_memory_gb = 8

# Authenticate with Azure
#credential = DefaultAzureCredential()
#token = credential.get_token("https://management.azure.com/.default").token
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSIsImtpZCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuYXp1cmUuY29tLyIsImlzcyI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2ZiZTYyMDgxLTA2ZDgtNDgxZC1iYWEwLTM0MTQ5Y2ZlZmE1Zi8iLCJpYXQiOjE3NTY5ODg5MDIsIm5iZiI6MTc1Njk4ODkwMiwiZXhwIjoxNzU2OTk0NDczLCJhY3IiOiIxIiwiYWNycyI6WyJwMSIsInVybjp1c2VyOnJlZ2lzdGVyc2VjdXJpdHlpbmZvIl0sImFpbyI6IkFYUUFpLzhaQUFBQUlQSlFDUEdTUkEydTVZNUgvS3hBbElrT0JlVVRxOWJZc1duNGJteDRFenpkeGlHcXQ4SXM1K3dEaGozRVVpN2lNb2t5ZzZYZG14N1lOTjRlWUhqblFreHZwMWhJRHlvRDRPYTRZMGJURS9laVpnV1ExOTZvMFRSUkdtSUFCVndEWUdqK1RvOHU4QUg4QlhJODFWRXREdz09IiwiYW1yIjpbInB3ZCIsInJzYSIsIm1mYSJdLCJhcHBpZCI6IjA0YjA3Nzk1LThkZGItNDYxYS1iYmVlLTAyZjllMWJmN2I0NiIsImFwcGlkYWNyIjoiMCIsImRldmljZWlkIjoiM2U0NjU0YWYtZjc5Ny00YzI2LThlZGQtZDAwNTE4NjBjNTAyIiwiZmFtaWx5X25hbWUiOiJDaG91cmFzaWEiLCJnaXZlbl9uYW1lIjoiQXNoaXNoIiwiZ3JvdXBzIjpbIjYxYzc1NDAwLTFkZjItNDk4MC04MTc3LTM1ZDUzOTZmZDczMiIsIjVhZjFiNDBhLTgyNDctNGE0NS05ZjhlLTIwZTlhMGNkYjYxNiIsImEyOTM0ZDExLWZlMTktNGQ2NC05MDIwLTgxZmIxNjY4NDBkNyIsIjc0YWNiNjE1LTFmMjEtNDA0YS1iMDlhLWM4MjllYzAwODIyZCIsIjk0N2IwYzFmLTdjMWEtNDg3ZS1iYjEwLTEyZDc0YzgxMmY1YyIsImZhNTExNDJmLWI4MDgtNDFhNi04YzYyLWRjYmJkZjkxYTM3OCIsIjFkYmQ1ZjNhLTE2ZTUtNDYxYi1iZDAxLWZjMjcyZGY0ZTQ3NCIsIjY1ZDg1OTQzLWJiZDctNGU4OS1iOWRlLTQ5Y2I1NzZiZGM4YyIsImU0YWY0NDQ4LTgzMjQtNDAyMC05MzAzLWQ2YTlkZDU2NDQzYyIsIjRhNWYyMjRkLWM4YTItNGIwNi1iN2E3LTdjZjFjNWJlZTU5NSIsImM0NDFkYzRkLWE0ZmItNDhiYS04OGI4LTU4N2YxMzA3N2NlMiIsIjhhMDY2NDUzLTY1MmItNGRjYi1hNjAyLTc1NTM1ZTllNWFlYyIsIjM0M2FlNzVjLWY2OWUtNDdlZS04NzVhLTFkNzcxMjQ3OTdlZCIsIjhkNDQ5YjZjLTY4NzktNGI2NS1hMmUyLTc2ODY4MDFkOTk4MSIsImNkNjE4YzcwLTBiMzktNDEzYi04Nzg3LWJmNWY3YWI3NjQyNyIsIjQyOGQwMDc1LTE1NGEtNGY4NC04YTI1LTY1NzQ0YWMwNWNmMiIsImM3ZmVkZDdmLTE5YWYtNDU1OS05MDBkLWRhNGQ3N2I1YWJhYiIsImM1YWQzNWJhLTcwZTctNGMwZi1hNDM0LTNhYWVkNjZmYjFjOSIsImJmNWU0MGJhLTZmMjgtNGU5Zi04YTVjLThkOGQ5ZmQwNTRhNSIsIjQxNTYxZGJmLTY5MjItNGMxMi04NmRjLTVmMTVlMmY1MjVlMyIsImRlMTZiNmM0LTZkNTAtNGRlNy05ZTE0LTMyOTA3YzJlM2Q0YyIsImMyNGFmMGM1LTk2YzAtNDBkMi04NmFkLTM4YjU0NzZmMzgzMCIsIjY3NTRiYWNjLWFiY2MtNDE2NC1iNjdlLTNkNDg3NTk1NTMyNCIsImMwYzJmYWQwLWM0ZDAtNDE1MS1iODQ0LTMwYWM4NzMwNjYwMyIsIjVjOGZiYmQ4LTQyOGQtNDEwNy1iYTQxLWZlOTkxOTA4M2E2NyIsImE2YzI5NWU5LTg0ZGMtNGVjOS04MTQ4LWUzNTMzYjA4NjEwYyIsImQ2NWZkZmVlLTc0YWYtNDg1Mi1iZTQ4LWNkM2ZiOTVkYzI0MSJdLCJpZHR5cCI6InVzZXIiLCJpcGFkZHIiOiIyNDAxOjQ5MDA6MWM3NTo1ZTM1OmUxMjQ6ODQxYjo0YTU1OmY3NTkiLCJuYW1lIjoiQ2hvdXJhc2lhLCBBc2hpc2giLCJvaWQiOiIyMTZkYzkxMy04YjkwLTQwZTgtOTliNy04ZjhhODFkZWJkODAiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMjEzNzM1NDQ5MS0xNDYwNTM5MTE2LTMyNTg2MzQ4LTIxNTA4MTMiLCJwdWlkIjoiMTAwMzIwMDQ3QUQ1QjE0MSIsInB3ZF91cmwiOiJodHRwczovL3BvcnRhbC5taWNyb3NvZnRvbmxpbmUuY29tL0NoYW5nZVBhc3N3b3JkLmFzcHgiLCJyaCI6IjEuQVFjQWdTRG0tOWdHSFVpNm9EUVVuUDc2WDBaSWYza0F1dGRQdWtQYXdmajJNQk1IQUFJSEFBLiIsInNjcCI6InVzZXJfaW1wZXJzb25hdGlvbiIsInNpZCI6IjAwM2RmYjQ5LWZlZmItZTdhYy1lNDRlLTc0MjZjMTE2ZDY0YiIsInN1YiI6IlNwcGJvNk5CVWZuTEJES0twcEtvZGpCd3VvakU3R0F2SUQwWDJHSkFXTjAiLCJ0aWQiOiJmYmU2MjA4MS0wNmQ4LTQ4MWQtYmFhMC0zNDE0OWNmZWZhNWYiLCJ1bmlxdWVfbmFtZSI6IkFzaGlzaC5DaG91cmFzaWFAbHlvbmRlbGxiYXNlbGwuY29tIiwidXBuIjoiQXNoaXNoLkNob3VyYXNpYUBseW9uZGVsbGJhc2VsbC5jb20iLCJ1dGkiOiIzTWRrNk9mOTVVQ0dUSk1KMHU5REFRIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXSwieG1zX2Z0ZCI6ImwwNTVCelpBeDRISTVUdWtJYXF6Vm5yYkhPc0dxN2RPTTVEbGtoTUcwdlVCZFhOemIzVjBhQzFrYzIxeiIsInhtc19pZHJlbCI6IjEgMTYiLCJ4bXNfdGNkdCI6MTM2NTUxODk2N30.LUxptcsLACsolH19oUDKSBJHbGOz7-Cp58eEEt9Eze86djzQpfVibt6iIdJYcGTTnLFLXqRk16Hj7Fk8bN7fru-YymQ4UKRb4p4FwCmz23Ea9CSWrLNRUuDKdxHUZn7S_77RlBpYYfJdiVH4W5qgzKg8rEDsfXvkmCvryUlZXHVJjxgG6jyu8Hwnnh8VlL2mySBOLStUHTWUZCsWyGZP0nWmPBU5IWHcNUz3IhFm8oyCD6g-7-Ui3p7HncllfoUCVtvr1-ICMcvTAGgoKIW5HcqZxRnUBEOYEiNvrJnEPaypQ3BawAp0yN1iL0o-q2avEMJWKSFpSDkLtVI1AGZVqg"
headers = {"Authorization": f"Bearer {token}"}

# Step 1: Get VM SKUs with vCPU & memory
compute_url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Compute/skus?api-version=2023-01-02"
vm_skus = []

while compute_url:
    resp = requests.get(compute_url, headers=headers).json()
    #print(resp)
    for item in resp.get("value", []):
        if item["resourceType"] == "virtualMachines" and region in item["locations"]:
            caps = {c["name"]: c["value"] for c in item.get("capabilities", [])}
            vcpu = int(caps.get("vCPUs", 0))
            memory = int(float(caps.get("MemoryGB", 0)))
            if vcpu == required_vcpu and memory == required_memory_gb:
                vm_skus.append(item["name"])
    compute_url = resp.get("nextLink")

print(f"Matching SKUs: {vm_skus}")

# Step 2: Get price from Azure Retail Prices API
for sku in vm_skus:
    price_url = (
        "https://prices.azure.com/api/retail/prices"
        f"?$filter=serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and armSkuName eq '{sku}'"
    )
    resp = requests.get(price_url).json()
    items = resp.get("Items", [])
    for item in items:
        print(f"SKU: {sku} | Location: {item['armRegionName']} | Price: {item['retailPrice']} {item['currencyCode']} per {item['unitOfMeasure']}")
        #print(f"SKU: {sku} | Location: {item['armRegionName']} | Price: {item['retailPrice']} {item['currencyCode']} per {item['unitPrice']} {item['unitOfMeasure']}")