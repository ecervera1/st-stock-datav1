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
            "Market Cap (B)": info.get("marketCap") / 1e9 if info.get("marketCap") else None, 
            "PE Ratio": info.get("trailingPE"),
            "PEG Ratio": info.get("pegRatio"),
            "Profit Margin": info.get("profitMargins"),
            "ROA": info.get("returnOnAssets"),
            "ROE": info.get("returnOnEquity"),
            "52W Range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
            "Div Yield": info.get("dividendYield"),
            "Price": info.get("currentPrice")
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

    # Plotting Financial Metrics and Revenue Comparison
    fig, axs = plt.subplots(len(tickers), 4, figsize=(24, 6 * len(tickers)))
    for i, ticker in enumerate(tickers):
        financial_metrics = fetch_financial_metrics(ticker)
        financials = get_financials(ticker)
        if financial_metrics and not financials.empty:
            # Financial Metrics
            profit_margin = financial_metrics["Profit Margin"]
            roa = financial_metrics["ROA"]
            roe = financial_metrics["ROE"]
            axs[i, 0].barh(["Profit Margin", "ROA", "ROE"], [profit_margin, roa, roe], color=['blue', 'green', 'red'])
            axs[i, 0].set_title(f"{ticker} Financial Metrics")

            # Revenue Comparison
            current_year_revenue = financials.loc["Total Revenue"][0] / 1e9
            previous_year_revenue = financials.loc["Total Revenue"][1] / 1e9
            growth = ((current_year_revenue - previous_year_revenue) / previous_year_revenue) * 100
            axs[i, 1].bar(["Last Year", "This Year"], [previous_year_revenue, current_year_revenue], color=['orange', 'blue'])
            axs[i, 1].set_title(f"{ticker} Revenue Comparison")
            axs[i, 1].text(1, current_year_revenue, f"{growth:.2f}%", ha='center')

            # Market Cap
            market_cap = stock_summaries[i].get("Market Cap (B)", 0)
            axs[i, 2].pie([market_cap, 100-market_cap], labels=[f"{market_cap}B", ""], startangle=90, counterclock=False)
            axs[i, 2].set_title(f"{ticker} Market Cap")

            # Price and 52-Week Range
            price = stock_summaries[i].get("Price", 0)
            low_52w = stock_summaries[i].get("52W Range").split(' - ')[0]
            high_52w = stock_summaries[i].get("52W Range").split(' - ')[1]
            axs[i, 3].axhline(y=0.5, xmin=0, xmax=1, color='black', linewidth=3)
            axs[i, 3].scatter(price, 0.5, color='red', s=200)
            axs[i, 3].annotate(f'${price}', (price, 0.5), fontsize=12, ha='center', va='bottom')
            axs[i, 3].set_xlim(float(low_52w), float(high_52w))
            axs[i, 3].axis('off')
            axs[i, 3].set_title(f"{ticker} 52-Week Range")

    st.pyplot(fig)
