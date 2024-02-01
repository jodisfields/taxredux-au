import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as web

# Function to fetch stock data
def fetch_stock_data(stock, start, end):
    df = web.DataReader(stock, data_source='yahoo', start=start, end=end)
    return df

# Function to calculate SMAs
def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

# Streamlit app layout
st.title('Investment Strategy Application')

# User input for stock symbol
stock = st.sidebar.text_input('Enter Stock Symbol', 'AAPL')

# Date input for range
start_date = st.sidebar.date_input('Start Date', pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('End Date', pd.to_datetime('2021-01-01'))

# Display stock data
if st.button('Show Data'):
    stock_data = fetch_stock_data(stock, start_date, end_date)
    short_sma = calculate_sma(stock_data, 40)
    long_sma = calculate_sma(stock_data, 100)

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(stock_data['Close'], label='Close Price')
    ax.plot(short_sma, label='40-Day SMA')
    ax.plot(long_sma, label='100-Day SMA')
    ax.set_title(f'{stock} Stock Price and SMA Crossover')
    ax.legend()

    st.pyplot(fig)

