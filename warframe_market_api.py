import requests
import json
import pandas as pd

wfm_url = "https://api.warframe.market/v2/orders/recent"
headers = {
    "Platform" : "pc",
    "Language" : "en",
    'content-type' : 'application/json'
}

response = requests.get(wfm_url, headers=headers)

try:
    response.raise_for_status()  # Check if the request was successful
except requests.exceptions.HTTPError as e:
    print("HTTP error occurred: ", e)

response_dict = json.loads(response.text)
orders = response_dict["data"]
df = pd.json_normalize(orders)

df = df.drop(columns=[col for col in df.columns if col.startswith("user.")])
df = df.drop(columns=["id", "perTrade", "visible", "createdAt", "updatedAt", "subtype"])

buy_df = df[df["type"] == "buy"]
sell_df = df[df["type"] == "sell"]
