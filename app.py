import streamlit as st
import requests
import time
import pandas as pd
import os
from dotenv import load_dotenv
import finnhub

def configure():
    load_dotenv()

"This function fetches the current stock price using the Finnhub API"
def fetch_stock_price(symbol, api_key):
    finnhub_client = finnhub.Client(api_key)

    res = finnhub_client.quote(symbol)

    # us = [item for item in res['result'] if item['symbol'] == symbol]

    return res['c']


def main():
    # Get api key from .env file
    configure()
    api_key = os.getenv('api_key')

    # Display title
    st.title("Real-time Stock Price Monitor")

    # Dropdown menu with sample stock tickers
    symbols = st.multiselect("Select Stocks", ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"])

    # Check if there are any symbols selected
    if symbols:
        # Display heading
        st.write('## Live Stock Prices: ')

        # Create a pandas dataframe to store stock data
        df = pd.DataFrame({'Symbol': symbols, 'Price': [0.0] * len(symbols)})

        # Creates space to display table
        table_placeholder = st.empty()

        while True:
            for symbol in symbols:
                try:
                    # Get the stock price for a given symbol
                    price = fetch_stock_price(symbol, api_key)
            
                    # Update the existing DataFrame
                    df.loc[df['Symbol'] == symbol, 'Price'] = price

                except Exception as e:
                    st.error(f"Error fetching price for {symbol}: {e}")

            # Update the table in place
            table_placeholder.table(df)
            time.sleep(5)

main()