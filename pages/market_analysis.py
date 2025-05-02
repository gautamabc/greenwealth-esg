"""
Market Analysis page for the Green Energy Stock Exchange Platform.
This page is automatically loaded by Streamlit's multi-page app feature.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf

from utils import (
    get_stock_data, 
    get_multiple_stocks_data,
    create_comparison_chart,
    get_sector_performance,
    generate_mock_esg_score
)
from config import GREEN_ENERGY_STOCKS, TIME_PERIODS

# Page configuration
st.set_page_config(
    page_title="Market Analysis | Green Energy Stock Exchange",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for time period if not exists
if 'selected_period' not in st.session_state:
    st.session_state.selected_period = "1mo"

# Market Analysis Page
st.title("Green Energy Market Analysis")

# Time period selection
st.sidebar.header("Time Period")
time_period = st.sidebar.selectbox(
    "Select Time Period",
    list(TIME_PERIODS.keys()),
    index=list(TIME_PERIODS.values()).index(st.session_state.selected_period)
)
selected_period = TIME_PERIODS[time_period]
st.session_state.selected_period = selected_period

# Performance Comparison
st.header("Performance Comparison")

# Allow multi-selection of stocks to compare
ticker_options = [f"{name} ({ticker})" for ticker, name, _ in GREEN_ENERGY_STOCKS]
default_selections = [
    f"First Solar (FSLR)", 
    f"Tesla, Inc. (TSLA)",
    f"NextEra Energy (NEE)",
    f"SolarEdge Technologies (SEDG)"
]

selected_companies = st.multiselect(
    "Select Companies to Compare",
    ticker_options,
    default=default_selections
)

selected_tickers = [company.split("(")[1].split(")")[0] for company in selected_companies]

if selected_tickers:
    # Get data for selected tickers
    comparison_data = get_multiple_stocks_data(selected_tickers, period=selected_period)
    
    if all(not df.empty for df in comparison_data.values()):
        st.subheader("Relative Performance Comparison")
        fig = create_comparison_chart(comparison_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Absolute price comparison
        st.subheader("Absolute Price Comparison")
        
        # Create a DataFrame with closing prices for all selected stocks
        price_data = pd.DataFrame()
        for ticker, df in comparison_data.items():
            price_data[ticker] = df['Close']
        
        # Plot absolute prices
        fig = px.line(
            price_data,
            x=price_data.index,
            y=price_data.columns,
            title="Stock Price Comparison"
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=500,
            legend_title="Stocks"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Loading comparison data...")
else:
    st.info("Please select at least one company to compare.")

# Sector Analysis
st.header("Sector Analysis")

# Get sector performance data
sector_perf = get_sector_performance()

if not sector_perf.empty:
    # Sector performance chart
    fig = px.bar(
        sector_perf,
        x='Sector',
        y='Performance',
        color='Performance',
        text_auto='.2f',
        color_continuous_scale=['red', 'green'],
        title="Green Energy Sector Performance (%)"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top performers by sector
    st.subheader("Top Performers by Sector")
    
    # Get performance data for all stocks
    performance_data = []
    for ticker, name, sector in GREEN_ENERGY_STOCKS:
        stock_data = get_stock_data(ticker, period=selected_period)
        if not stock_data.empty:
            start_price = stock_data['Close'].iloc[0]
            end_price = stock_data['Close'].iloc[-1]
            change_pct = ((end_price / start_price) - 1) * 100
            performance_data.append({
                "Ticker": ticker,
                "Name": name,
                "Sector": sector,
                "Performance": change_pct,
                "Current Price": end_price
            })
    
    if performance_data:
        performance_df = pd.DataFrame(performance_data)
        
        # Group by sector and show top performer in each
        sectors = performance_df['Sector'].unique()
        
        sector_tops = []
        for sector in sectors:
            sector_data = performance_df[performance_df['Sector'] == sector]
            top_performer = sector_data.iloc[sector_data['Performance'].argmax()]
            sector_tops.append(top_performer)
        
        top_df = pd.DataFrame(sector_tops)
        
        # Display top performers by sector
        st.dataframe(
            top_df[["Sector", "Name", "Ticker", "Performance", "Current Price"]],
            column_config={
                "Performance": st.column_config.NumberColumn(
                    "Performance",
                    format="%.2f%%"
                ),
                "Current Price": st.column_config.NumberColumn(
                    "Current Price",
                    format="$%.2f"
                )
            },
            use_container_width=True
        )
        
        # Selected sector deep dive
        st.subheader("Sector Deep Dive")
        
        # Allow selecting a sector for detailed analysis
        selected_sector = st.selectbox(
            "Select Sector for Analysis",
            sectors
        )
        
        # Show all stocks in that sector with their performance
        sector_stocks = performance_df[performance_df['Sector'] == selected_sector]
        sector_stocks = sector_stocks.sort_values("Performance", ascending=False)
        
        st.dataframe(
            sector_stocks[["Ticker", "Name", "Performance", "Current Price"]],
            column_config={
                "Performance": st.column_config.NumberColumn(
                    "Performance",
                    format="%.2f%%"
                ),
                "Current Price": st.column_config.NumberColumn(
                    "Current Price",
                    format="$%.2f"
                )
            },
            use_container_width=True
        )
        
        # Plot performance of all stocks in the sector
        sector_tickers = sector_stocks['Ticker'].tolist()
        sector_data = get_multiple_stocks_data(sector_tickers, period=selected_period)
        
        if all(not df.empty for df in sector_data.values()):
            st.subheader(f"{selected_sector} Stocks Performance Comparison")
            fig = create_comparison_chart(sector_data)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Loading performance data...")
else:
    st.info("Loading sector analysis data...")

# Market Trends
st.header("Market Trends")

# Correlation matrix of green energy stocks
st.subheader("Stock Correlation Matrix")

# Get a subset of stocks for correlation analysis
correlation_tickers = ["FSLR", "ENPH", "SEDG", "RUN", "TSLA", "NIO", "NEE", "BEP", "PLUG"]
correlation_data = {}

for ticker in correlation_tickers:
    stock_data = get_stock_data(ticker, period="1mo")
    if not stock_data.empty:
        correlation_data[ticker] = stock_data['Close']

if correlation_data:
    # Create DataFrame with closing prices
    corr_df = pd.DataFrame(correlation_data)
    
    # Calculate correlation matrix
    corr_matrix = corr_df.corr().round(2)
    
    # Create heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        title="Correlation Between Green Energy Stocks"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Interpretation Guide:**
    - Values close to 1.0 indicate strong positive correlation (stocks move together)
    - Values close to -1.0 indicate strong negative correlation (stocks move in opposite directions)
    - Values near 0 indicate little to no correlation
    """)
else:
    st.info("Loading correlation data...")

# ESG Analysis
st.header("ESG Analysis")

# Generate ESG scores for all stocks
esg_data = []
for ticker, name, sector in GREEN_ENERGY_STOCKS:
    score = generate_mock_esg_score(ticker)
    esg_data.append({
        "Ticker": ticker,
        "Name": name,
        "Sector": sector,
        "ESG Score": score['total'],
        "Environmental": score['environmental'],
        "Social": score['social'],
        "Governance": score['governance'],
        "Rating": score['rating']
    })

if esg_data:
    esg_df = pd.DataFrame(esg_data)
    
    # Show ESG scores for all companies
    st.dataframe(
        esg_df.sort_values("ESG Score", ascending=False),
        column_config={
            "ESG Score": st.column_config.ProgressColumn(
                "ESG Score",
                min_value=0,
                max_value=100,
                format="%d"
            ),
            "Environmental": st.column_config.ProgressColumn(
                "Environmental",
                min_value=0,
                max_value=100,
                format="%d"
            ),
            "Social": st.column_config.ProgressColumn(
                "Social",
                min_value=0,
                max_value=100,
                format="%d"
            ),
            "Governance": st.column_config.ProgressColumn(
                "Governance",
                min_value=0,
                max_value=100,
                format="%d"
            ),
        },
        use_container_width=True
    )
    
    # Average ESG scores by sector
    st.subheader("Average ESG Scores by Sector")
    
    sector_esg = esg_df.groupby('Sector').agg({
        "ESG Score": "mean",
        "Environmental": "mean",
        "Social": "mean",
        "Governance": "mean"
    }).reset_index()
    
    fig = px.bar(
        sector_esg,
        x='Sector',
        y=['Environmental', 'Social', 'Governance'],
        title="ESG Component Scores by Sector",
        barmode='group'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # ESG vs Performance Analysis
    st.subheader("ESG Score vs. Stock Performance")
    
    # Merge ESG data with performance data
    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        combined_df = pd.merge(esg_df, perf_df, on=["Ticker", "Name", "Sector"])
        
        # Create scatter plot
        fig = px.scatter(
            combined_df,
            x="ESG Score",
            y="Performance",
            color="Sector",
            size="Current Price",
            hover_name="Name",
            hover_data=["Ticker", "Rating"],
            title="ESG Score vs. Stock Performance"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **Analysis:**
        This chart helps visualize the relationship between ESG scores and stock performance.
        Positive correlation might suggest that companies with better ESG practices tend to perform better in the market.
        """)
else:
    st.info("Loading ESG analysis data...")

# Volume Analysis
st.header("Trading Volume Analysis")

# Get volume data for major green energy stocks
volume_tickers = ["FSLR", "ENPH", "TSLA", "NEE", "PLUG"]
volume_data = {}

for ticker in volume_tickers:
    stock_data = get_stock_data(ticker, period=selected_period)
    if not stock_data.empty:
        volume_data[ticker] = stock_data['Volume']

if volume_data:
    # Create DataFrame with volume data
    vol_df = pd.DataFrame(volume_data)
    
    # Create volume chart
    fig = px.line(
        vol_df,
        title="Trading Volume Comparison"
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Volume",
        height=500,
        legend_title="Stocks"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Average daily volume
    st.subheader("Average Daily Trading Volume")
    
    avg_volume = vol_df.mean().reset_index()
    avg_volume.columns = ["Ticker", "Average Volume"]
    
    # Get company names for display
    ticker_to_name = {}
    for ticker, name, _ in GREEN_ENERGY_STOCKS:
        ticker_to_name[ticker] = name
    
    avg_volume["Company"] = avg_volume["Ticker"].map(ticker_to_name)
    
    # Sort by average volume
    avg_volume = avg_volume.sort_values("Average Volume", ascending=False)
    
    # Display as bar chart
    fig = px.bar(
        avg_volume,
        x="Ticker",
        y="Average Volume",
        title="Average Daily Trading Volume",
        hover_data=["Company"]
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Loading volume analysis data...")

# Footer
st.markdown("---")
st.caption("Green Energy Stock Exchange Platform | Market Analysis")
