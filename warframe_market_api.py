import requests
import json
import pandas as pd


def api_call(url, custom_header):
    try:
        response = requests.get(url, headers=custom_header)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.HTTPError as e:
        print("HTTP error occurred: ", e)
    
    return json.loads(response.text)

def normalize_df(response_dict):
    orders = response_dict["data"]
    df = pd.json_normalize(orders)
    return df

def main():
    order_url = "https://api.warframe.market/v2/orders/recent"
    item_url = "https://api.warframe.market/v2/items"
    headers = {
        "Platform" : "pc",
        "Language" : "en",
        'content-type' : 'application/json'
    }
    orders = api_call(order_url, headers)
    items = api_call(item_url, headers)

    orders_df = normalize_df(orders)
    items_df = normalize_df(items)

    orders_df["item_name"] = orders_df["itemId"].map(items_df.set_index("id")["i18n.en.name"])

    aggregated_df = orders_df.groupby(["type", "item_name"]).agg(
            quantity=("quantity", "sum"),
            average_price=("platinum", "mean"),
            lowest_price=("platinum", "min"),
            highest_price=("platinum", "max")   
    ).reset_index()

    print(aggregated_df.head(n=30))

    return 0

if __name__ == "__main__":
    main()