import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.patheffects as path_effects


# Function to scrape stock data
def scrape_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    growth_ratio = info.get("revenueGrowth")
    pe_ratio = info.get("trailingPE")
    earnings_growth = info.get("revenueGrowth")

    data = {
        "Market Cap (B)": info.get("marketCap") / 1e9 if info.get("marketCap") else None,  # convert to billions
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



    #CREATING CHARTS ************************************************************

    # Create a figure with subplots: X columns (Ticker, Market Cap, Revenue, Financial Metrics) for each ticker
    fig, axs = plt.subplots(len(tickers), 6, figsize=(32, 8 * len(tickers)))

    for i, ticker in enumerate(tickers):
    def scrape_stock_data(ticker):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="1y")
    
            data = {
                "Ticker": ticker,
                "Market Cap": info.get("marketCap") / 1e9,  # Convert to billions
                "Revenue": info.get("revenueGrowth"),
                "Profit Margin": info.get("profitMargins"),
                "ROA": info.get("returnOnAssets"),
                "ROE": info.get("returnOnEquity"),
                "Current Price": info.get("currentPrice"),
                "52 Week Low": history['Low'].min(),
                "52 Week High": history['High'].max(),
            }
            return data
        except Exception as e:
            print(f"Error scraping data for {ticker}: {str(e)}")
            return None
    
    # Adjust bar width for less padding
    bar_width = 1
    
    # Create a figure with subplots: X columns (Ticker, Market Cap, Revenue, Financial Metrics) for each ticker
    fig, axs = plt.subplots(len(tickers), 6, figsize=(32, 8 * len(tickers)))
    
    for i, ticker in enumerate(tickers):
        # Ticker Labels (First Column)
        axs[i, 0].axis('off')
        axs[i, 0].text(0.5, 0.5, ticker, ha='center', va='center', fontsize=20)
    
        # Market Cap Visualization (Second Column)
        ax1 = axs[i, 1]
        stock_data = scrape_stock_data(ticker)
        if stock_data:
            market_cap_in_billions = stock_data["Market Cap"]
            circle = plt.Circle((0.5, 0.5), 0.4, color='lightblue')
            ax1.add_artist(circle)
            text = ax1.text(0.5, 0.5, f"${market_cap_in_billions:.2f}B", ha='center', va='center', fontsize=55, fontweight='bold', color='white')
            text.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='black'),
                path_effects.Normal()
            ])
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
            ax1.axis('off')
    
        # Revenue Comparison (Third Column)
        ax2 = axs[i, 2]
        financials = scrape_stock_data(ticker)
        if financials:
            current_year_revenue = financials["Revenue"]
            previous_year_revenue = financials["Revenue"]
            current_year_revenue_billion = current_year_revenue / 1e9
            previous_year_revenue_billion = previous_year_revenue / 1e9
            growth = ((current_year_revenue_billion - previous_year_revenue_billion) / previous_year_revenue_billion) * 100
            line_color = 'green' if growth > 0 else 'red'
            bars = ax2.bar(["2022", "2023"], [previous_year_revenue_billion, current_year_revenue_billion], color=['blue', 'orange'])
            ax2.set_title(f"{ticker} Revenue Comparison (2022 vs 2023)")
            ax2.set_ylim(0, max(previous_year_revenue_billion, current_year_revenue_billion) * 1.2)
            for bar in bars:
                yval = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, yval * .95, round(yval, 2), ha='center', va='top', fontsize=18, fontweight='bold', color='white')
            for i, bar in enumerate(bars):
                ax2.text(bar.get_x() + bar.get_width()/2, -0.08, ["2022", "2023"][i], ha='center', va='bottom', fontsize=18, fontweight='bold', color='white')
            ax2.plot(["2022", "2023"], [previous_year_revenue_billion, current_year_revenue_billion], color=line_color, marker='o', linestyle='-', linewidth=2)
            ax2.text(1, current_year_revenue_billion * 1.05, f"{round(growth, 2)}%", color=line_color, ha='center', va='bottom', fontsize=16)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.spines['bottom'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            ax2.set_xticks([])
            ax2.set_yticks([])
    
        # Financial Metrics (Fourth Column)
        ax3 = axs[i, 3]
        metrics = scrape_stock_data(ticker)
        if metrics:
            profit_margin = metrics["Profit Margin"]
            roa = metrics["ROA"]
            roe = metrics["ROE"]
            bar_width = 1
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.barh([1, 2, 3], [profit_margin, roa, roe], height=bar_width, color=['#A3C5A8', '#B8D4B0', '#C8DFBB'])
            bar_labels = ["Profit Margin", "ROA", "ROE"]
            for bar, label in zip(bars, bar_labels):
                ax.text(bar.get_x() - 1, bar.get_y() + bar.get_height()/2, label, ha='right', va='center', fontsize=14, fontweight='bold', color='black')
            for bar, value in zip(bars, [profit_margin, roa, roe]):
                if value != 0:
                    text_x = value - 5 if value < 0 else value - 1
                    ax.text(text_x, bar.get_y() + bar.get_height()/2, f"{value:.2f}%", ha='left' if value < 0 else 'right', va='center', fontsize=14, color='black')
            ax.set_title(f"{ticker} - Financial Metrics")
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels([])
            ax.set_yticklabels([])

        # Price and 52 Week Range (Fifth Column)
        ax4 = axs[i, 4]
        stock_data = scrape_stock_data(ticker)
        if stock_data:
            # Calculate padding for visual clarity
            padding = (stock_data["52 Week High"] - stock_data["52 Week Low"]) * 0.05
            ax4.set_xlim(stock_data["52 Week Low"] - padding, stock_data["52 Week High"] + padding)
            ax4.axhline(y=0.5, xmin=0, xmax=1, color='black', linewidth=3)
            ax4.scatter(stock_data["Current Price"], 0.5, color='red', s=200)
            ax4.axis('off')
            ax4.annotate(f'${stock_data["Current Price"]:.2f}', xy=(stock_data["Current Price"], 0.5), fontsize=50, color='red', fontweight='bold',
                        ha='center', va='bottom', xytext=(0, 10), textcoords='offset points')
            ax4.annotate(f'${stock_data["52 Week Low"]:.2f}', xy=(stock_data["52 Week Low"], 0.5), fontsize=35, color='black', fontweight='bold',
                        ha='left', va='top', xytext=(5, -20), textcoords='offset points')
            ax4.annotate(f'${stock_data["52 Week High"]:.2f}', xy=(stock_data["52 Week High"], 0.5), fontsize=35, color='black', fontweight='bold',
                        ha='right', va='top', xytext=(-5, -20), textcoords='offset points')
        plt.tight_layout()
        st.pyplot(fig)
