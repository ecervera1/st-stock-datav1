import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

# Function to scrape summary stock data
def scrape_stock_summary(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "Current Price": info.get("currentPrice"),
            "Market Cap (B)": info.get("marketCap") / 1e9 if info.get("marketCap") else None, 
            "PE Ratio": info.get("trailingPE"),
            "PEG Ratio": info.get("pegRatio"),
            "Profit Margin": info.get("profitMargins"),
            "ROA": info.get("returnOnAssets"),
            "ROE": info.get("returnOnEquity"),
            "52W Range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
            "Div Yield": info.get("dividendYield"),
            "Beta": info.get("beta"),
            "Forward Annual Dividend Yield": info.get("dividendYield") or 0,
            "EPS per Year": info.get("trailingEps"),
            "Revenue Growth": info.get("revenueGrowth"),
            "Earnings Growth": info.get("earningsGrowth")
            
        }
    except Exception as e:
        st.error(f"Error fetching summary data for {ticker}: {e}")
        return {}

# Function to fetch financial metrics
def fetch_financial_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "Profit Margin": info.get("profitMargins"),
            "ROA": info.get("returnOnAssets"),
            "ROE": info.get("returnOnEquity")
        }
    except Exception as e:
        st.error(f"Error fetching financial metrics for {ticker}: {e}")
        return {}

# Function to fetch stock performance data
def fetch_stock_performance(tickers, start_date, end_date):
    try:
        data = yf.download(tickers, start=start_date, end=end_date)
        return data
    except Exception as e:
        st.error(f"Error fetching stock performance data: {e}")
        return pd.DataFrame()

# Function to get financials
def get_financials(ticker):
    try:
        stock = yf.Ticker(ticker)
        financials = stock.financials
        return financials
    except Exception as e:
        st.error(f"Error fetching financials for {ticker}: {e}")
        return pd.DataFrame()

# Streamlit App Layout
st.title('Portfolio Management - Stock Comparative Analysis')

# Input for stock tickers
user_input = st.text_input("Enter stock tickers separated by commas", "LLY, ABT, MRNA, JNJ, BIIB, BMY, PFE, AMGN, WBA")

# Input for date range
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2024-01-22"))

if st.button('Run'):
    # Split the user input into a list of tickers
    tickers = [ticker.strip().upper() for ticker in user_input.split(',')]

    # Fetch and Plot Stock Performance
    performance_data = fetch_stock_performance(tickers, start_date, end_date)
    if not performance_data.empty:
        st.title('Stock Performance Chart')
        st.markdown(f'({start_date} - {end_date})')
        st.line_chart(performance_data['Adj Close'])

    # Fetch Summary Stock Data
    stock_summaries = [scrape_stock_summary(ticker) for ticker in tickers]
    stock_summary_df = pd.DataFrame(stock_summaries, index=tickers).transpose()
    stock_summary_df.fillna('-', inplace=True)
    st.title('Stock Data')
    st.table(stock_summary_df)


