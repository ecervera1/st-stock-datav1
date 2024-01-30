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

    # Function to scrape market cap data
    def scrape_market_cap(ticker):
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get("marketCap")
        return market_cap

    # Function to get financials
    def get_financials(ticker):
        stock = yf.Ticker(ticker)
        financials = stock.financials
        return financials

    # Function to scrape financial metrics data
    def scrape_financial_metrics(ticker):
        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            "Profit Margin": info.get("profitMargins"),
            "ROA": info.get("returnOnAssets"),
            "ROE": info.get("returnOnEquity"),
        }
        return data

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
        market_cap = scrape_market_cap(ticker)
        market_cap_in_billions = market_cap / 1_000_000_000

        circle = plt.Circle((0.5, 0.5), 0.4, color='lightblue')
        ax1.add_artist(circle)

        # Create a shadow effect for the text
        text = ax1.text(0.5, 0.5, f"{market_cap_in_billions:.2f}B", ha='center', va='center', fontsize=55, fontweight='bold', color='white')
        text.set_path_effects([
            path_effects.Stroke(linewidth=2, foreground='black'),
            path_effects.Normal()
        ])

        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')

        # Revenue Comparison (Third Column) 222222222222222222222222222222222222222222222222222
        ax2 = axs[i, 2]
        financials = get_financials(ticker)
        current_year_revenue = financials.loc["Total Revenue"][0]
        previous_year_revenue = financials.loc["Total Revenue"][1]

        current_year_revenue_billion = current_year_revenue / 1e9
        previous_year_revenue_billion = previous_year_revenue / 1e9
        growth = ((current_year_revenue_billion - previous_year_revenue_billion) / previous_year_revenue_billion) * 100

        line_color = 'green' if growth > 0 else 'red'

        bars = ax2.bar(["2022", "2023"], [previous_year_revenue_billion, current_year_revenue_billion], color=['blue', 'orange'])
        ax2.set_title(f"{ticker} Revenue Comparison (2022 vs 2023)")

        # Adjust Y-axis limits to leave space above the bars
        ax2.set_ylim(0, max(previous_year_revenue_billion, current_year_revenue_billion) * 1.2)

        # Adding value labels inside of the bars at the top in white
        for bar in bars:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, yval * .95, round(yval, 2), ha='center', va='top', fontsize=18, fontweight='bold', color='white')

        # Adding year labels inside of the bars toward the bottom
        for i, bar in enumerate(bars):
            ax2.text(bar.get_x() + bar.get_width()/2, -0.08, ["2022", "2023"][i], ha='center', va='bottom', fontsize=18, fontweight='bold', color='white')

        # Adding growth line with color based on direction
        ax2.plot(["2022", "2023"], [previous_year_revenue_billion, current_year_revenue_billion], color=line_color, marker='o', linestyle='-', linewidth=2)
        ax2.text(1, current_year_revenue_billion * 1.05, f"{round(growth, 2)}%", color=line_color, ha='center', va='bottom', fontsize=16)

        # Remove axes lines
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        # Remove x and y ticks
        ax2.set_xticks([])
        ax2.set_yticks([])

        # Financial Metrics (Fourth Column) 3333333333333333333333333333333333333333333333333333
        ax3 = axs[i, 3]

        def scrape_stock_data2(ticker):
            stock = yf.Ticker(ticker)
            info = stock.info

            data = {
                "Profit Margin": info.get("profitMargins"),
                "ROA": info.get("returnOnAssets", 0),
                "ROE": info.get("returnOnEquity"),
            }
            return data

        # Adjust bar width for less padding
        bar_width = 1

        # Iterate through tickers
        for ticker in tickers:
            # Scrape data for the ticker
            stock_data = scrape_stock_data2(ticker)

            # Extract Profit Margin, ROA, and ROE values and convert to percentage
            profit_margin = stock_data["Profit Margin"] * 100
            roa = stock_data["ROA"] * 100
            roe = stock_data["ROE"] * 100

        # Create a horizontal bar chart with three bars side by side
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh([1, 2, 3], [profit_margin, roa, roe], height=bar_width, color=['#A3C5A8', '#B8D4B0', '#C8DFBB'])

        bar_labels = ["Profit Margin", "ROA", "ROE"]
        for bar, label in zip(bars, bar_labels):
            ax.text(bar.get_x() - 1, bar.get_y() + bar.get_height()/2, label, ha='right', va='center', fontsize=14, fontweight='bold', color='black')

        # Add data values as text next to each bar (excluding 0 values)
        for bar, value in zip(bars, [profit_margin, roa, roe]):
            if value != 0:  # Check if the value is not equal to 0
                text_x = value - 5 if value < 0 else value - 1
                ax.text(text_x, bar.get_y() + bar.get_height()/2, f"{value:.2f}%", ha='left' if value < 0 else 'right', va='center', fontsize=14, color='black')

        # Set the title
        ax.set_title(f"{ticker} - Financial Metrics")

        # Remove axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Remove x and y ticks and labels
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # Price and 52 Week Range (Fifth Column) 44444444444444444444444444444444444444444444444444444
        ax4 = axs[i, 4]


        #index 5 - current price and 52 week range 555555555555555555555555555555555555555555555
        #ax5 = axs[i, 5]
        
        # Function to scrape data for a single stock
        def scrape_stock_data(ticker):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                history = stock.history(period="1y")

                data = {
                    "Ticker": ticker,
                    "Current Price": info.get("currentPrice"),
                    "52 Week Low": history['Low'].min(),
                    "52 Week High": history['High'].max(),
                    "PE Ratio": info.get("trailingPE"),
                    "Beta": info.get("beta"),
                    "Forward Annual Dividend Yield": info.get("dividendYield") or 0,
                    "Market Cap": info.get("marketCap") / 1e9,  # Convert to billions
                    "Sales": info.get("revenueGrowth"),
                    "Profit Margin": info.get("profitMargins"),
                    "ROA": info.get("returnOnAssets"),
                    "ROE": info.get("returnOnEquity"),
                    "EPS per Year": info.get("trailingEps"),
                    "52 Week Range": f"{info.get('fiftyTwoWeekLow')} - {info.get('fiftyTwoWeekHigh')}",
                }
                return data
            except Exception as e:
                print(f"Error scraping data for {ticker}: {str(e)}")
                return None

        # Scrape data for all specified stocks
        stock_data = [scrape_stock_data(ticker) for ticker in tickers if scrape_stock_data(ticker) is not None]

        # Convert list of dicts to a DataFrame
        stock_df = pd.DataFrame(stock_data)

        # Create separate 52 Week Range plots for each ticker and save them individually
        for index, row in stock_df.iterrows():
            fig, ax5 = plt.subplots(figsize=(8, 4))
            # Calculate padding for visual clarity
            padding = (row["52 Week High"] - row["52 Week Low"]) * 0.05
            ax5.set_xlim(row["52 Week Low"] - padding, row["52 Week High"] + padding)
        
            # Draw a horizontal line for the 52-week range
            ax5.axhline(y=0.5, xmin=0, xmax=1, color='black', linewidth=3)  # Use y=0.5 to place the line in the middle of the y-axis
        
            # Plot the Current Price as a red dot
            ax5.scatter(row["Current Price"], 0.5, color='red', s=200)  # Use y=0.5 to match the line's y-axis
        
            # Remove axes
            ax5.axis('off')
        
            # Annotate Current Price
            ax5.annotate(f'${row["Current Price"]:.2f}', xy=(row["Current Price"], 0.5), fontsize=50, color='red', fontweight ='bold',
                        ha='center', va='bottom', xytext=(0, 10), textcoords='offset points')
        
            # Annotate 52 Week Low and High
            ax5.annotate(f'${row["52 Week Low"]:.2f}', xy=(row["52 Week Low"], 0.5), fontsize=35, color='black', fontweight='bold',
                        ha='left', va='top', xytext=(5, -20), textcoords='offset points')
            ax5.annotate(f'${row["52 Week High"]:.2f}', xy=(row["52 Week High"], 0.5), fontsize=35, color='black', fontweight='bold',
                        ha='right', va='top', xytext=(-5, -20), textcoords='offset points')
        
            st.pyplot(fig)
