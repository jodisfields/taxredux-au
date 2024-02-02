import streamlit as st
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components
from plotly import graph_objs as go
from datetime import date
import pandas as pd

# Set page config
st.set_page_config(page_title="TaxRedux AU", layout="wide", initial_sidebar_state="expanded")

# Define global variables
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

# Define tax brackets
CURRENT_BRACKETS = [(18200, 0), (45000, 0.19), (120000, 0.325), (180000, 0.37), (float('inf'), 0.45)]
NEW_BRACKETS = [(18200, 0), (45000, 0.16), (135000, 0.30), (190000, 0.37), (float('inf'), 0.45)]

# Function to calculate tax
def calculate_tax(income, brackets):
    tax = 0
    for i in range(len(brackets) - 1):
        lower, rate = brackets[i]
        upper = brackets[i + 1][0]
        if income > upper:
            tax += (upper - lower) * rate
        else:
            tax += (income - lower) * rate
            break
    return tax

# Function to load stock data
@st.cache_data
def load_data(ticker):
    try:
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Failed to download data for {ticker}: {e}")
        return None

# Function to plot raw stock data
def plot_raw_data(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Open"], name="Open"))
    fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Close"))
    fig.layout.update(title_text="Stock Price Data", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

# Main page
def main_page():
    st.title("Welcome to TaxRedux AU")
    st.markdown("### Your One-Stop Solution for Tax Calculations and Stock Analysis in Australia 🇦🇺")

# Tax Calculation Page
def tax_calculation_page():
    st.title("Australian Tax Calculator")
    income = st.number_input("Enter your annual income (AUD)", min_value=0.0, format="%.2f")

    if income:
        current_tax = calculate_tax(income, CURRENT_BRACKETS)
        new_tax = calculate_tax(income, NEW_BRACKETS)
        st.markdown(f"**Current Tax Payable:** AUD {current_tax:,.2f}")
        st.markdown(f"**Projected Tax Payable (New Brackets):** AUD {new_tax:,.2f}")

# Stock Analysis Page
def stock_analysis_page():
    st.title("Stock Data Analysis and Forecasting")
    st.markdown("Select a stock, view historical data and get a forecast.")

    ticker = st.text_input("Enter the stock ticker (e.g., AAPL, MSFT):").upper()
    if ticker:
        data = load_data(ticker)
        if data is not None and not data.empty:
            plot_raw_data(data)

            # Prophet Forecast
            df_train = data[['Date', 'Close']]
            df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

            m = Prophet()
            m.fit(df_train)
            future = m.make_future_dataframe(periods=365)  # 1 year
            forecast = m.predict(future)

            st.subheader("Forecast for the next year")
            fig1 = plot_plotly(m, forecast)
            st.plotly_chart(fig1)

            st.subheader("Forecast components")
            fig2 = plot_components(m, forecast)
            st.write(fig2)

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Home", "Australian Tax Calculator", "Stock Data Analysis"))

if page == "Home":
    main_page()
elif page == "Australian Tax Calculator":
    tax_calculation_page()
elif page == "Stock Data Analysis":
    stock_analysis_page()
