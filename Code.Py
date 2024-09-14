import requests
import pandas as pd
import json
import time
import os


class OptionChain:
    def __init__(self, symbol='NIFTY', timeout=5) -> None:
        self.__url = "https://www.nseindia.com/api/option-chain-indices?symbol={}".format(symbol)
        self.__session = requests.sessions.Session()
        self.__session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu Linux x86_64; rv:102.0) Gecko/20100181 Firefox/182.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.8,en-GB;q=0.7"
        })
        self.__timeout = timeout

    def fetch_data(self, expiry_date=None, starting_strike_price=None, number_of_rows=2):
        try:
            response = self.__session.get(url=self.__url, timeout=self.__timeout)
            response.raise_for_status()  # Raise an exception for HTTP errors

            data = response.json()
            df = pd.json_normalize(data['records']['data'])

            if expiry_date is not None:
                df = df[df['expiryDate'] == expiry_date]
            if starting_strike_price is not None:
                df = df[df['strikePrice'] >= starting_strike_price]

            return df.head(number_of_rows)
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return pd.DataFrame()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Unexpected error: {e}")
            return pd.DataFrame()

    def save_to_excel(self, data, filename="option_chain.xlsx"):
        """
        Saves the OptionChain data to an excel file.

        Args:
            data (pandas.DataFrame): The data to be saved.
            filename (str, optional): The filename of the excel file. Defaults to "option_chain.xlsx".
        """
        data.to_excel(filename, index=False)  # Save without index column

if __name__ == '__main__':
    obj = OptionChain(symbol='Nifty')
    data = obj.fetch_data()

    # Specify the desired directory
    save_directory = os.path.join(os.path.expanduser("~/Desktop"), "data")
    os.makedirs(save_directory, exist_ok=True)  # Create the directory if it doesn't exist

    filename = os.path.join(save_directory, "option_chain.xlsx")
    if not data.empty:
        obj.save_to_excel(data, filename)
        print(f"Option chain data saved to: {filename}")
    else:
        print("No data retrieved for the specified symbol.")
