import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

# Set your subscription ID
subscription_id = "74ebef29-9863-4c57-bd13-b510f4824772"
# Choose a target region (example: "eastus", "centralindia", "westeurope")
TARGET_REGION = "eastus"

# Authenticate
credential = DefaultAzureCredential()
compute_client = ComputeManagementClient(credential, subscription_id)

# Fetch all SKUs
skus = compute_client.resource_skus.list()

rows = []
for sku in skus:
    if sku.resource_type == "virtualMachines" and TARGET_REGION in sku.locations:
        # Extract CPU and memory from capabilities
        caps = {cap.name: cap.value for cap in sku.capabilities}
        vcpus = caps.get("vCPUs", None)
        memory = caps.get("MemoryGB", None)

        rows.append({
            "Name": sku.name,
            "Family": sku.family,
            "Region": TARGET_REGION,
            "vCPUs": vcpus,
            "MemoryGB": memory,
            "Tier": sku.tier
        })

# Convert to DataFrame
df = pd.DataFrame(rows)

# Save to CSV
output_file = f"C:\\workspace\\cloud-cost-expert-agent\\export\\azure_vm_skus_{TARGET_REGION}.csv"
df.to_csv(output_file, index=False)

print(f" Exported {len(df)} VM SKUs available in {TARGET_REGION} to {output_file}")
