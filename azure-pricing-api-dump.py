import requests
import json
import os

# Output file for cached catalog
OUTPUT_FILE = "C:\workspace\cloud-cost-expert-agent\export\azure_retail_prices.json"

# Base URL
BASE_URL = "https://prices.azure.com/api/retail/prices"

def fetch_all_prices():
    all_items = []
    url = BASE_URL
    page = 1

    while url:
        print(f"Fetching page {page} ...")
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception(f"Error fetching {url}: {resp.text}")

        data = resp.json()
        items = data.get("Items", [])
        all_items.extend(items)

        url = data.get("NextPageLink")  # pagination
        page += 1

    return all_items

def save_catalog(data, file_path=OUTPUT_FILE):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} items to {file_path}")

def load_catalog(file_path=OUTPUT_FILE):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    # Try to load cache
    catalog = load_catalog()
    if catalog:
        print(f"Loaded {len(catalog)} cached items from {OUTPUT_FILE}")
    else:
        print("No cache found, downloading fresh catalog...")
        catalog = fetch_all_prices()
        save_catalog(catalog)