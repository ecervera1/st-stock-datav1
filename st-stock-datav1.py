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
            "52W Low": info.get("fiftyTwoWeekLow"),
            "52W High":info.get("fiftyTwoWeekHigh"),
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
    num_subplots = len(tickers)
    figsize_width =  26
    figsize_height = num_subplots * 4  # Height of the entire figure

    # Create a figure with subplots: X columns (Ticker, Market Cap, Revenue, Financial Metrics...) for each ticker
    fig, axs = plt.subplots(num_subplots, 5, figsize=(figsize_width, figsize_height))
    
    for i, ticker in enumerate(tickers):

        # Function to scrape market cap data
        def scrape_market_cap(ticker):
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get("marketCap")
            return market_cap
    
        # Get market cap data
        market_caps = {ticker: scrape_market_cap(ticker) for ticker in tickers}
        
        # Find the largest market cap for scaling
        max_market_cap = max(market_caps.values())
        
        #Scrape data for the ticker
        stock_data = scrape_stock_data(ticker)
        
        # Extract Profit Margin, ROA, and ROE values and convert to percentage
        profit_margin = stock_data["Profit Margin"] * 100
        roa = stock_data["ROA"] * 100 if isinstance(stock_data["ROA"], (float, int)) and stock_data["ROA"] > 0 else 0
        roe = stock_data["ROE"] * 100 if isinstance(stock_data["ROE"], (float, int)) and stock_data["ROE"] > 0 else 0


        # Ticker Labels (First Column)
        axs[i, 0].axis('off')
        axs[i, 0].text(0.5, 0.5, ticker, ha='center', va='center', fontsize=30)

        # Market Cap Visualization (Second Column)
        ax1 = axs[i, 1]
        market_cap = market_caps.get(ticker, 0)
        relative_size = market_cap / max_market_cap if max_market_cap > 0 else 0
        circle = plt.Circle((0.5, 0.5), relative_size * 0.5, color='lightblue')
        ax1.add_artist(circle)
        ax1.set_aspect('equal', adjustable='box')
        text = ax1.text(0.5, 0.5, f"{market_cap / 1e9:.2f}B", ha='center', va='center', fontsize=20)
        text.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        
        # Adjust bar width for less padding
        bar_width = 1
        
        # ROE ROA and PM      
        ax2 = axs[i, 2]
        bars = ax2.barh([1, 2, 3], [profit_margin, roa, roe], height=bar_width, color=['#A3C5A8', '#B8D4B0', '#C8DFBB'])

        

        bar_labels = ["Profit Margin", "ROA", "ROE"]
        for bar, label in zip(bars, bar_labels):
            ax2.text(bar.get_x() - 1, bar.get_y() + bar.get_height()/2, label, ha='right', va='center', fontsize=14, fontweight='bold', color='black')

        # Add data values as text next to each bar (excluding 0 values)
        for bar, value in zip(bars, [profit_margin, roa, roe]):
            if value != 0:  # Check if the value is not equal to 0
                text_x = value - 5 if value < 0 else value - 1
                ax2.text(text_x, bar.get_y() + bar.get_height()/2, f"{value:.2f}%", ha='left' if value < 0 else 'right', va='center', fontsize=16, color='black')

        #ax2.set_aspect('equal', adjustable='box')
        # Set the title
        #ax2.set_title(f"{ticker} - Financial Metrics")

        # Remove axes
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)

        # Remove x and y ticks and labels
        ax2.set_xticks([])
        ax2.set_yticks([])
        ax2.set_xticklabels([])
        ax2.set_yticklabels([])

        # Revenue Comparison (Third Column)
        ax3 = axs[i, 3]
        financials = get_financials(ticker)
        current_year_revenue = financials.loc["Total Revenue"][0]
        previous_year_revenue = financials.loc["Total Revenue"][1]
    
        current_year_revenue_billion = current_year_revenue / 1e9
        previous_year_revenue_billion = previous_year_revenue / 1e9
        growth = ((current_year_revenue_billion - previous_year_revenue_billion) / previous_year_revenue_billion) * 100
    
        line_color = 'green' if growth > 0 else 'red'
    
        bars = ax3.bar(["2022", "2023"], [previous_year_revenue_billion, current_year_revenue_billion], color=['blue', 'orange'])
        #ax3.set_title(f"{ticker} Revenue Comparison (2022 vs 2023)")
    
        # Adjust Y-axis limits to leave space above the bars
        ax3.set_ylim(0, max(previous_year_revenue_billion, current_year_revenue_billion) * 1.2)
    
        # Adding value labels inside of the bars at the top in white
        for bar in bars:
            yval = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2, yval * .95, round(yval, 2), ha='center', va='top', fontsize=18, fontweight='bold', color='white')
    
        # Adding year labels inside of the bars toward the bottom
        # The 'i' in the for loop below should be changed to avoid conflicts
        for bar_idx, bar in enumerate(bars):
            ax3.text(bar.get_x() + bar.get_width()/2, -0.08, ["2022", "2023"][bar_idx], ha='center', va='bottom', fontsize=18, fontweight='bold', color='white')
    
        # Adding growth line with color based on direction
        ax3.plot(["2022", "2023"], [previous_year_revenue_billion, current_year_revenue_billion], color=line_color, marker='o', linestyle='-', linewidth=2)
        ax3.text(1, current_year_revenue_billion * 1.05, f"{round(growth, 2)}%", color=line_color, ha='center', va='bottom', fontsize=16)
    
        # Remove axes lines
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.spines['bottom'].set_visible(False)
        ax3.spines['left'].set_visible(False)
    
        # Remove x and y ticks
        ax3.set_xticks([])
        ax3.set_yticks([])

        # 52-Week Range (Fourth Column)
        ax4 = axs[i, 4]
        stock_data = scrape_stock_data(ticker)
        current_price = stock_data["Current Price"]
        week_low = stock_data["52W Low"]
        week_high = stock_data["52W High"]
    
        # Calculate padding for visual clarity
        padding = (week_high - week_low) * 0.05
        ax4.set_xlim(week_low - padding, week_high + padding)
    
        # Draw a horizontal line for the 52-week range
        ax4.axhline(y=0.5, xmin=0, xmax=1, color='black', linewidth=3)
    
        # Plot the Current Price as a red dot
        ax4.scatter(current_price, 0.5, color='red', s=200)
    
        # Annotations and labels
        ax4.annotate(f'${current_price:.2f}', xy=(current_price, 0.5), fontsize=16, color='red', ha='center', va='bottom', xytext=(0, 10), textcoords='offset points')
        ax4.annotate(f'${week_low:.2f}', xy=(week_low, 0.5), fontsize=16, color='black', ha='left', va='top', xytext=(5, -20), textcoords='offset points')
        ax4.annotate(f'${week_high:.2f}', xy=(week_high, 0.5), fontsize=16, color='black', ha='right', va='top', xytext=(-5, -20), textcoords='offset points')
    
        # Remove axes
        ax4.axis('off')


    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
