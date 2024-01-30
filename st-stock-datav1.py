import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

# Function to scrape summary stock data
def scrape_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    growth_ratio = info.get("revenueGrowth")
    pe_ratio = info.get("trailingPE")
    earnings_growth = info.get("revenueGrowth")

    data = {
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
            "Forward Annual Dividend Yield": info.get("dividendYield") or "-",
            "EPS per Year": info.get("trailingEps"),
            "Revenue Growth": info.get("revenueGrowth"),
            "Earnings Growth": info.get("earningsGrowth")
            
        }
    return data

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
# Function to fetch stock performance data
def fetch_stock_performance(tickers, start_date, end_date):
    # Fetch the historical close prices and volumes for the tickers
    data = yf.download(tickers, start=start_date, end=end_date)
    return data

# Streamlit app layout
st.title('Portfolio Management - Stock Comparative Analysis')

# Input for stock tickers
user_input = st.text_input("Enter stock tickers separated by commas", "LLY, ABT, MRNA, JNJ, BIIB, BMY, PFE, AMGN, WBA")

# Input for date range
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2024-01-22"))

# Button to run the scraper and plot stock performance
if st.button('Run'):
    # Split the user input into a list of tickers
    tickers = [ticker.strip() for ticker in user_input.split(',')]

    # Plot stock performance
    data = fetch_stock_performance(tickers, start_date, end_date)

    st.title('Stock Performance Chart')
    st.markdown(f'({start_date} - {end_date})')
    # Plotting the interactive line chart
    st.line_chart(data['Adj Close'])
    st.title('Stock Data')

    # Create an empty list to store dictionaries of stock data
    stock_data_list = []


    # Loop through each ticker, scrape the data, and add it to the list
    for ticker in tickers:
        try:
            ticker_data = scrape_stock_data(ticker)
            stock_data_list.append(ticker_data)
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

    # Create a DataFrame from the list of dictionaries
    stock_data_df = pd.DataFrame(stock_data_list, index=tickers)

    # Transpose the DataFrame
    stock_data_transposed = stock_data_df.transpose()

    stock_data_transposed.fillna('-', inplace=True)

    for col in stock_data_transposed.columns:
        if col != "52W Range":  # Exclude the "52W Range" column
            stock_data_transposed[col] = stock_data_transposed[col].apply(
                lambda x: f'{x:.2f}' if isinstance(x, float) else x)


    # Display the DataFrame as a table
    st.table(stock_data_transposed)

    # Creating Charts
    # Create a figure with subplots: X columns (Ticker, Market Cap, Revenue, Financial Metrics...) for each ticker
    fig, axs = plt.subplots(len(tickers), 6, figsize=(32, 8 * len(tickers)))

    # Create a figure with subplots: X columns (Ticker, Market Cap, Revenue, Financial Metrics...) for each ticker
    fig, axs = plt.subplots(len(tickers), 6, figsize=(24, 8 * len(tickers)))

    for i, ticker in enumerate(tickers):
        # Ticker Labels (First Column)
        axs[i, 0].axis('off')
        axs[i, 0].text(0.5, 0.5, ticker, ha='center', va='center', fontsize=20)

        # Market Cap Visualization (Second Column)
        ax1 = axs[i, 1]
        def scrape_market_cap(ticker):
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get("marketCap")
            return market_cap
        market_cap = scrape_market_cap(ticker)
        market_cap_in_billions = market_cap / 1_000_000_000

        circle = plt.Circle((0.5, 0.5), 0.4, color='lightblue')
        ax1.add_artist(circle)

        # Create a shadow effect for the text
        text = ax1.text(0.5, 0.5, f"{market_cap_in_billions:.2f}B", ha='center', va='center', fontsize=55, fontweight='bold', color='white')
        text.set_path_effects([
            path_effects.withStroke(linewidth=2, foreground='black'),
            path_effects.Normal()  # Corrected from 'path_effects.Normal()'
        ])


        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        
        

    #plt.subplots_adjust(wspace=0.5)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.subplots_adjust(wspace=0.5, hspace=0.5)
    st.pyplot(fig)

