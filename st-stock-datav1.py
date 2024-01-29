import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pandas.plotting import table
import base64
#import matplotlib.path_effects as path_effects




# Function to scrape stock data
def scrape_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    growth_ratio = info.get("revenueGrowth")
    pe_ratio = info.get("trailingPE")
    earnings_growth = info.get("revenueGrowth")

    data = {
        "Market Cap (B)": info.get("marketCap") / 1e9 if info.get("marketCap") else None,
        "Sales": growth_ratio,
        "Profit Margin": info.get("profitMargins"),
        "ROA": info.get("returnOnAssets"),
        "ROE": info.get("returnOnEquity"),
        "Trailing EPS": info.get("trailingEps"),
        "Forward EPS": info.get("forwardEps"),
        "52W Range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
        "PE": pe_ratio,
        "PEG Ratio": info.get("pegRatio"),
        "Beta": info.get("beta"),
        "Div Yield": info.get("dividendYield"),
        "Price": info.get("currentPrice"),
        "Revenue Growth": info.get("revenueGrowth"),
        "Earnings Growth": info.get("earningsGrowth")
    }
    return data

# Function to fetch stock performance data
def fetch_stock_performance(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)
    return data

# Function to scrape market cap data
def scrape_market_cap(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    market_cap = info.get("marketCap")
    return market_cap

# Streamlit app layout
st.title('Portfolio Management - Stock Comparative Analysis')

# Input for stock tickers
user_input = st.text_input("Enter stock tickers separated by commas", "LLY, ABT, MRNA, JNJ, BIIB, BMY, PFE, AMGN, WBA")

# Input for date range
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2024-01-22"))

# Button to run the scraper and plot stock performance
if st.button('Run'):
    tickers = [ticker.strip() for ticker in user_input.split(',')]
    data = fetch_stock_performance(tickers, start_date, end_date)

    st.title('Stock Performance Chart')
    st.markdown(f'({start_date} - {end_date})')
    st.line_chart(data['Adj Close'])
    st.title('Stock Data')

    stock_data_df = pd.DataFrame()
    for ticker in tickers:
        try:
            ticker_data = scrape_stock_data(ticker)
            stock_data_df = stock_data_df.append(pd.DataFrame([ticker_data], index=[ticker]))
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

    stock_data_transposed = stock_data_df.transpose()

    for col in stock_data_df.columns:
        if col not in ["52W Range"]:
            stock_data_df[col] = stock_data_df[col].apply(lambda x: f'{x:.2f}' if isinstance(x, float) else x)

    st.title('Stock Data Table')
    st.table(stock_data_transposed)

    # List of stocks for market cap
    market_cap_tickers = ["LLY", "ABT", "MRNA", "JNJ", "BIIB", "BMY", "PFE", "AMGN", "WBA"]

    # Get market cap data
    market_caps = {ticker: scrape_market_cap(ticker) for ticker in market_cap_tickers}

    # Find the largest market cap for scaling
    max_market_cap = max(market_caps.values())

    # Prepare data for the table
    market_cap_data = []
    for ticker, cap in market_caps.items():
        market_cap_in_billions = cap / 1_000_000_000
        market_cap_data.append({
            "Ticker": ticker,
            "Market Cap (B)": f"{market_cap_in_billions:.2f}B",
            "Relative Size": cap / max_market_cap
        })

    # Display the Market Cap Data as a table
    st.title('Market Capitalization Data')
    market_cap_df = pd.DataFrame(market_cap_data)
    st.table(market_cap_df)
