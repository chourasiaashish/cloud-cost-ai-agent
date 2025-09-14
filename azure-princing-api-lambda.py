import awswrangler as wr
import pandas as pd
import requests
import boto3
from io import StringIO
import logging
import urllib3
import json
from typing import Dict, Any
from http import HTTPStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#http = urllib3.PoolManager()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    def get_named_parameter(event, name):
        return next(item for item in event['parameters'] if item['name'] == name)['value']

    def find_sku(df, vcpus, memory_gb):
        """Find SKU(s) that match vCPU and memory."""
        #print(f" vCPUs= {vcpus} and memory_gb {memory_gb} ")
        vcpus=int(vcpus)
        memory_gb=float(memory_gb)
        #print(f" vCPUs type= {type(vcpus)} and memory_gb type {type(memory_gb)} ")
        matches = df[(df["vCPUs"] == vcpus) & (df["MemoryGB"] == memory_gb)]
        #print(f" matches= {matches} ")
        return matches

    def get_price(sku_name, region):
        """Query Azure Retail Prices API for a given SKU and region."""
        url = (
            "https://prices.azure.com/api/retail/prices"
            f"?$filter=serviceName eq 'Virtual Machines'"
            f" and armRegionName eq '{region}'"
            f" and armSkuName eq '{sku_name}'"
        )
        #Example: https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Virtual Machines' and armRegionName eq 'eastus' and armSkuName eq 'Standard_D2s_v3'
        results = []
        while url:
            resp = requests.get(url)
            data = resp.json()
            #items = data.get("Items", [])
            #if not items:
            #    return None
            
            #first = items[0]  # take first match only
            for item in data.get("Items", []):
                product_name = item.get("productName", "")
                unit_price = item.get("unitPrice", 0)
                os_type = "Windows" if "Windows" in product_name else "Linux"
                if operatingSystem != os_type: continue #   filter by OS type
                results.append({
                    "sku": sku_name,
                    "productName": product_name,
                    "osType": os_type,
                    "meterName": item.get("meterName"),
                    "unitPrice": unit_price,
                    "currency": item.get("currencyCode"),
                    "region": item.get("armRegionName")
                })
            url = data.get("NextPageLink")  # pagination
        return results           
    try:
        action_group = event['actionGroup']
        function = event['function']
        message_version = event.get('messageVersion', 1)

        if function == 'get_azure_vm_cost':
            region = "eastus"
            #region = get_named_parameter(event, "region")       # e.g., "eastus"
            #sku_name = get_named_parameter(event, "skuName")   # e.g., "Standard_D2s_v3"
            # Input requirement: e.g., 4 vCPU and 16 GB
            vcpus = get_named_parameter(event, "vcpu")
            memory = get_named_parameter(event, "memory")
            operatingSystem = get_named_parameter(event, "operatingSystem") #Need to consume this parameter to avoid error

            # S3 bucket & key where your CSV is stored
            BUCKET_NAME = "cloud-cost-agent-bucket"
            OBJECT_KEY = "azure_vm_skus_eastus.csv"

            def load_csv_from_s3(bucket, key):
                """Read CSV file from S3 into a pandas DataFrame"""
                s3_client = boto3.client("s3")
                obj = s3_client.get_object(Bucket=bucket, Key=key)
                body = obj["Body"].read().decode("utf-8")
                df = pd.read_csv(StringIO(body))
                return df

            # Load CSV from S3
            df = load_csv_from_s3(BUCKET_NAME, OBJECT_KEY)

            # CSV file generated from previous script
            #CSV_FILE = "C:/workspace/cloud-cost-expert-agent/export/azure_vm_skus_eastus.csv"
            # Load CSV of SKUs
            #df = pd.read_csv(CSV_FILE)

            # Ensure numeric columns are properly typed
            df["vCPUs"] = pd.to_numeric(df["vCPUs"], errors="coerce")
            df["MemoryGB"] = pd.to_numeric(df["MemoryGB"], errors="coerce")


            matches = find_sku(df,vcpus, memory)
            matches = matches[0:1]  # limit to first 1 matches for brevity
            if matches.empty:
                print(f" No SKU found with {vcpus} vCPUs and {memory} GB in {region}")
            else:
                for _, row in matches.iterrows():
                    sku_name = row["Name"]
                    print(f" Found SKU: {sku_name} ({vcpus} vCPUs, {memory} GB)")
                    prices = get_price(sku_name, region)
                    if prices:
                        for p in prices[0:1]:  # limit to show first 1 options
                            print(f" productName:{p['productName']} - meterName:{p['meterName']} - sku:{p['sku']} = unitPrice:{p['unitPrice']} {p['currency']}/hour")
                    else:
                        print("   No pricing info found")

                    response_body = {
                        'TEXT': {
                            'body': f'Azure VM Cost: {p['unitPrice']} {p['currency']}/hour for sku name {p['sku']} in {region}'
                        }
                }
            # if "Items" in data and len(data["Items"]) > 0:
            #     price = data["Items"][0].get("retailPrice", "N/A")
            #     unit = data["Items"][0].get("unitOfMeasure", "")
            #     response_body = {
            #         'TEXT': {
            #             'body': f'Azure VM Cost: {price} USD/{unit} for {sku_name} in {region}'
            #         }
            #     }
            # else:
            #     response_body = {
            #         'TEXT': {
            #             'body': f'No pricing data found for {sku_name} in {region}'
            #         }
            #     }
        else:
            print(" function is not get_azure_vm_cost")
            response_body = {
                'TEXT': {
                    'body': f'The function {function} is not implemented yet.'
                }
            }

        return {
            'response': {
                'actionGroup': action_group,
                'function': function,
                'functionResponse': {
                    'responseBody': response_body
                }
            },
            'messageVersion': message_version
        }

    except KeyError as e:
        logger.error("Missing required field: %s", str(e))
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'body': f'Error: {str(e)}'
        }
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': f'Internal server error: {str(e)}'
        }