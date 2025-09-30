import streamlit as st
import requests
import time
import pandas as pd
import os
from dotenv import load_dotenv
import finnhub
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# load the dotenv variables, most importantly the api key
def configure():
    load_dotenv()

# This function fetches the current stock price using the Finnhub API
def fetch_stock_price(client, symbol):

    # get the stock quote data for the given symbol and store it in "res"
    res = client.quote(symbol)

    # us = [item for item in res['result'] if item['symbol'] == symbol]

    # return the value that corresponds with key 'c', which is the stock price
    return res['c']

# This function returns insider info for the given stock
def fetch_mspr(client, symbol):

    # get today's date
    today = datetime.today()

    # calculate the date on the first day of the current month
    first_day = today.replace(day=1).strftime("%Y-%m-%d")

    # calculate the date for the last day of the current month.
    # (even if the date is in the future, it will default to this month)
    next_month = today.replace(day=28) + timedelta(days=4)
    last_day = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d") 

    res = client.stock_insider_sentiment(symbol, first_day, last_day)

    if res['data'] == []:
        return False

    return res['data'][-1]['mspr']


def graph_insider_sentiment(client, symbol):

    today = datetime.today()

    last_year = today - timedelta(days=365)

    today = today.strftime("%Y-%m-%d")
    last_year = last_year.strftime("%Y-%m-%d")

    res = client.stock_insider_sentiment(symbol, last_year, today)

    yearly_sentiment = {}

    for i in res['data']:
        month_year = str(i['year']) + "-" + str(i['month'])
        if not month_year in yearly_sentiment:
            yearly_sentiment[month_year] = []
        yearly_sentiment[month_year].append(round(i['mspr'], 2))

    fig, ax = plt.subplots()
    ax.plot(list(yearly_sentiment.keys()), list(yearly_sentiment.values()), marker="o")
    ax.set_xlabel("Month")
    ax.set_ylabel("Buy/Sell Rating")
    ax.set_title("Insider Sentiment in Recent History")

    st.pyplot(fig)


# def color_mspr(val):
    if val > 0:
        color = 'green'
    elif val < 0:
        color = 'red'
    else:
        color = 'black'
    return f'color: {color}'


def main():
    # Get api key from .env file
    configure()
    api_key = os.getenv('api_key')

    # Display title
    st.title("Real-time Stock Price Monitor")

    client = finnhub.Client(api_key)

    # Dropdown menu with every single US stock
    us_symbols = client.stock_symbols('US')  # returns list of dicts
    symbol_list = [item['symbol'] for item in us_symbols]

    # Sort the list alphabetically
    symbol_list.sort()

    selected_symbols = st.multiselect("Select Stocks", symbol_list)

    # Check if there are any symbols selected
    if selected_symbols:

        # Display heading
        st.write('## Live Stock Prices: ')

        # Create a pandas dataframe to store stock data
        df = pd.DataFrame({'Symbol': selected_symbols, 'Price': [0.0] * len(selected_symbols),
                           'Insider Sentiment Available?': "" * len(selected_symbols), 
                           'Monthly Share Purchase Ratio': [0.0] * len(selected_symbols)})

        # Creates space to display table
        table_placeholder = st.empty()

        table_placeholder.dataframe(df.style.format({
            "Price": "{:.2f}",
            "Monthly Share Purchase Ratio": "{:.2f}"
        }))
        
        for symbol in selected_symbols:
            try:
                insider_sentiment = fetch_mspr(client, symbol)

                if insider_sentiment == False:
                    # Update the existing DataFrame
                    df.loc[df['Symbol'] == symbol, 'Insider Sentiment Available?'] = "No"
                    df.loc[df['Symbol'] == symbol, 'Monthly Share Purchase Ratio'] = 0
                else:
                    # Update the existing DataFrame
                    df.loc[df['Symbol'] == symbol, 'Insider Sentiment Available?'] = "Yes"
                    df.loc[df['Symbol'] == symbol, 'Monthly Share Purchase Ratio'] = insider_sentiment

            except Exception as e:
                st.error(f"Error fetching insider sentiment for {symbol}: {e}")

            try:
                graph_insider_sentiment(client, symbol)

            except Exception as e:
                st.error(f"Error graphing insider sentiment for {symbol}: {e}")

        while True:
            for symbol in selected_symbols:
                try:
                    # Get the stock price for a given symbol
                    price = fetch_stock_price(client, symbol)
            
                    # Update the existing DataFrame
                    df.loc[df['Symbol'] == symbol, 'Price'] = price

                except Exception as e:
                    st.error(f"Error fetching price for {symbol}: {e}")

                

            # Update the table in place
            table_placeholder.dataframe(df.style.format({
                "Price": "{:.2f}",
                "Monthly Share Purchase Ratio": "{:.2f}"
            }))

            time.sleep(1)

main()