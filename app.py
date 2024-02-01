import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
from datetime import date

# Set page config
st.set_page_config(layout="wide")

# Define global variables
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Function to calculate tax (placeholder logic)
def calculate_tax(income):
    # Implement tax calculation logic based on Australian tax brackets
    # ...
    return tax_payable

# Function to load stock data with new caching mechanism
@st.experimental_memo
def load_data(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Failed to download data for {ticker}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

# Function to plot raw stock data
def plot_raw_data(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Open"], name="stock_open"))
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="stock_close"))
    fig.layout.update(title_text="Time Series Data with Rangeslider", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

# Tax Calculation Page
def tax_calculation_page():
    st.title("Tax Calculation")
    income = st.number_input("Enter your annual income", min_value=0)
    tax_payable = calculate_tax(income)
    st.write(f"Your estimated tax payable is: ${tax_payable}")

# Stock Analysis and Forecasting Page
def stock_forecast_page():
    st.title("Stock Forecast")
    selected_stock = st.selectbox("Select dataset for prediction", ("AAPL", "GOOG", "MSFT", "AMZN"))  # Example stocks
    n_years = st.slider("Years of prediction:", 1, 5)
    period = n_years * 365

    data = load_data(selected_stock)

    if data.empty or data.shape[0] < 2:
        st.error("Not enough data to perform forecasting.")
        return

    # Prepare data for forecasting
    df_train = data[["Date", "Close"]]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    st.subheader("Forecast Data")
    st.write(forecast.tail())

    plot_raw_data(data)

    st.write(f"Forecast plot for {n_years} years")
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)

    st.write("Forecast components")
    fig2 = m.plot_components(forecast)
    st.write(fig2)

# Define page navigation
page_names_to_funcs = {
    "Tax Calculation": tax_calculation_page,
    "Stock Forecast": stock_forecast_page,
    # Additional pages can be added here
}

# Sidebar for navigation
selected_page = st.sidebar.selectbox("Select a page", list(page_names_to_funcs.keys()))
page_names_to_funcs[selected_page]()

