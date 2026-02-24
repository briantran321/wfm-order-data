import requests
import json

wfm_url = "https://api.warframe.market/v2/orders/recent"
headers = {
    "Platform" : "pc",
    "Crossplay" : "true",
    "Language" : "en",
    'content-type' : 'application/json'
}

response = requests.get(wfm_url, headers=headers)

try:
    response.raise_for_status()  # Check if the request was successful
except requests.exceptions.HTTPError as e:
    print("HTTP error occurred: ", e)

data = response.json()
print(data)

