import requests
import json
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout
from PyQt6.QtCore import QAbstractTableModel, Qt

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
    
# PyQt6 DataFrame GUI reads in dataframe
class PandasModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._df.columns[section])
            else:
                return str(self._df.index[section])
        return None

# GUI layout for the application
class DataFrameWindow(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.setWindowTitle("WFM Orders")
        self.resize(900, 600)
        widget = QWidget()
        layout = QVBoxLayout()
        self.table = QTableView()
        self.model = PandasModel(df)
        self.table.setModel(self.model)
        layout.addWidget(self.table)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

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

    # Show GUI
    app = QApplication([])
    window = DataFrameWindow(aggregated_df)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()

