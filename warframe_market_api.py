import requests
import json
import pandas as pd

# Calls upon warframe market api and returns a json object.
def api_call(url, custom_header):
    try:
        response = requests.get(url, headers=custom_header)
        response.raise_for_status()  # Check if the request was successful
    except requests.exceptions.HTTPError as e:
        print("HTTP error occurred: ", e) # Prints HTTP errors if they occur
    
    return json.loads(response.text)

# Normalizes the json response from the api call and returns a pandas dataframe
def normalize_df(response_dict):
    orders = response_dict["data"]
    df = pd.json_normalize(orders)
    return df

def main():
    order_url = "https://api.warframe.market/v2/orders/recent" # API endpoint for 500 recent orders
    item_url = "https://api.warframe.market/v2/items" # API endpoint for all items in the game
    headers = {
        "Platform" : "pc",
        "Language" : "en",
        'content-type' : 'application/json'
    }
    orders = api_call(order_url, headers)
    items = api_call(item_url, headers)

    orders_df = normalize_df(orders)
    items_df = normalize_df(items)

    # Swaps the itemId in the orders dataframe with the actual item names
    orders_df["item_name"] = orders_df["itemId"].map(items_df.set_index("id")["i18n.en.name"])

    # Aggregates orders by sell/buy & item names, then tallies quantity, average, lowest, and highest price for each item
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