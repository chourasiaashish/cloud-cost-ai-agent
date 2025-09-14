import boto3
import json

# Create a Pricing client (always use us-east-1 for pricing)
client = boto3.client("pricing", region_name="us-east-1")
memory = "32 GiB"
print(memory)
# Example: Get on-demand Linux m5.large price in US East (N. Virginia)
response = client.get_products(
    ServiceCode="AmazonEC2",
    Filters=[
        #{"Type": "TERM_MATCH", "Field": "instanceType", "Value": "m5.large"},
        {"Type": "TERM_MATCH", "Field": "vcpu", "Value": "8"},
        {"Type": "TERM_MATCH", "Field": "memory", "Value": memory},
        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
        {"Type": "TERM_MATCH", "Field": "location", "Value": "US East (N. Virginia)"},
        {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
        {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
    ],
    MaxResults=1
)

#print("Raw response:", json.dumps(response, indent=2))
# Parse the pricing JSON
price_item = json.loads(response["PriceList"][0])
sku = list(price_item["terms"]["OnDemand"].keys())[0]
instanceType=price_item["product"]["attributes"]["instanceType"]
price_dimensions = price_item["terms"]["OnDemand"][sku]["priceDimensions"]
price_per_unit = price_dimensions[list(price_dimensions.keys())[0]]["pricePerUnit"]["USD"]
print(f"On-Demand price for {instanceType} Linux in US East (N. Virginia): ${price_per_unit}/hour")
#print(json.dumps(price_item, indent=2))
