import requests
import json
import pandas as pd

order_url = "https://api.warframe.market/v2/orders/recent"
item_url = "https://api.warframe.market/v2/items"
headers = {
    "Platform" : "pc",
    "Language" : "en",
    'content-type' : 'application/json'
}

order_response = requests.get(order_url, headers=headers)

try:
    order_response.raise_for_status()  # Check if the request was successful
except requests.exceptions.HTTPError as e:
    print("HTTP error occurred: ", e)


order_response_dict = json.loads(order_response.text)
orders = order_response_dict["data"]
df = pd.json_normalize(orders)

df = df.drop(columns=[col for col in df.columns if col.startswith("user.")])
df = df.drop(columns=["id", "perTrade", "visible", "createdAt", "updatedAt", "subtype"])

item_response = requests.get(item_url, headers=headers)
try:
    item_response.raise_for_status()  # Check if the request was successful
except requests.exceptions.HTTPError as e:
    print("HTTP error occurred: ", e)

item_response_dict = json.loads(item_response.text)
item_list = item_response_dict["data"]
item_df = pd.json_normalize(item_list)

df["item_name"] = df["itemId"].map(item_df.set_index("id")["i18n.en.name"])

aggregated_df = df.groupby(["type", "item_name"]).agg(
        quantity=("quantity", "sum"),
        average_price=("platinum", "mean"),
        lowest_price=("platinum", "min"),
        highest_price=("platinum", "max")   
).reset_index()

print(aggregated_df.head(n=30))