"""
Company Details page for the Green Energy Stock Exchange Platform.
This page is automatically loaded by Streamlit's multi-page app feature.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf

from utils import (
    get_stock_data, 
    get_stock_info,
    create_price_chart,
    create_esg_radar_chart,
    generate_mock_esg_score,
    format_large_number
)
from config import GREEN_ENERGY_STOCKS, TIME_PERIODS, DEFAULT_PORTFOLIO_BALANCE

# Page configuration
st.set_page_config(
    page_title="Company Details | Green Energy Stock Exchange",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for selected ticker and time period if not exists
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "FSLR"

if 'selected_period' not in st.session_state:
    st.session_state.selected_period = "1mo"

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = DEFAULT_PORTFOLIO_BALANCE

if 'transaction_history' not in st.session_state:
    st.session_state.transaction_history = []

# Sidebar selections
st.sidebar.header("Company Selection")
ticker_options = [f"{name} ({ticker})" for ticker, name, _ in GREEN_ENERGY_STOCKS]
selected_company = st.sidebar.selectbox(
    "Select Company",
    ticker_options,
    index=next((i for i, opt in enumerate(ticker_options) if st.session_state.selected_ticker in opt), 0)
)
selected_ticker = selected_company.split("(")[1].split(")")[0]
st.session_state.selected_ticker = selected_ticker

st.sidebar.header("Time Period")
time_period = st.sidebar.selectbox(
    "Select Time Period",
    list(TIME_PERIODS.keys()),
    index=list(TIME_PERIODS.values()).index(st.session_state.selected_period)
)
selected_period = TIME_PERIODS[time_period]
st.session_state.selected_period = selected_period

# Company Details Page
# Get company info
info = get_stock_info(selected_ticker)
company_name = info.get('longName', selected_ticker) if info else selected_ticker

st.title(f"{company_name} ({selected_ticker})")

# Company metadata
if info:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Price",
            f"${info.get('currentPrice', 0):.2f}",
            f"{info.get('regularMarketChangePercent', 0):.2f}%"
        )
    
    with col2:
        st.metric(
            "Market Cap",
            format_large_number(info.get('marketCap', 0)),
            None
        )
    
    with col3:
        st.metric(
            "52 Week Range",
            f"${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}",
            None
        )

# Stock price chart
st.subheader("Stock Price History")
stock_data = get_stock_data(selected_ticker, period=selected_period)

if not stock_data.empty:
    fig = create_price_chart(stock_data, selected_ticker, company_name)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error(f"Could not load stock data for {selected_ticker}")

# Company info and ESG scores
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Company Overview")
    
    if info and 'longBusinessSummary' in info:
        st.write(info['longBusinessSummary'])
    else:
        st.write("No company description available.")
    
    # Company stats
    if info:
        stats_cols = st.columns(3)
        
        with stats_cols[0]:
            st.metric("P/E Ratio", f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A", None)
            st.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A", None)
        
        with stats_cols[1]:
            st.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}", None)
            st.metric("52 Week Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}", None)
        
        with stats_cols[2]:
            st.metric("Volume", f"{info.get('volume', 0):,}", None)
            st.metric("Avg Volume", f"{info.get('averageVolume', 0):,}", None)
    
    # Financial Information
    st.subheader("Financial Information")
    
    if info:
        fin_cols = st.columns(3)
        
        with fin_cols[0]:
            st.metric("Revenue", format_large_number(info.get('totalRevenue', 0)), None)
            st.metric("Gross Profit", format_large_number(info.get('grossProfits', 0)), None)
        
        with fin_cols[1]:
            st.metric("Profit Margin", f"{info.get('profitMargins', 0) * 100:.2f}%" if info.get('profitMargins') else "N/A", None)
            st.metric("Operating Margin", f"{info.get('operatingMargins', 0) * 100:.2f}%" if info.get('operatingMargins') else "N/A", None)
        
        with fin_cols[2]:
            st.metric("Return on Equity", f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get('returnOnEquity') else "N/A", None)
            st.metric("Return on Assets", f"{info.get('returnOnAssets', 0) * 100:.2f}%" if info.get('returnOnAssets') else "N/A", None)

with col2:
    st.subheader("ESG Score")
    
    # Get ESG data
    esg_data = generate_mock_esg_score(selected_ticker)
    
    # Display ESG score
    st.metric(
        "Total ESG Score",
        f"{esg_data['total']}/100",
        esg_data['rating']
    )
    
    # ESG breakdown
    fig = create_esg_radar_chart(esg_data)
    st.plotly_chart(fig, use_container_width=True)
    
    # ESG component scores
    st.write(f"Environmental: {esg_data['environmental']}/100")
    st.write(f"Social: {esg_data['social']}/100")
    st.write(f"Governance: {esg_data['governance']}/100")
    
    # ESG Rating explanation
    st.markdown(f"""
    **{esg_data['rating']} Rating Explanation:**
    
    Companies with {'an excellent' if esg_data['rating'] == 'Excellent' else 'a ' + esg_data['rating'].lower()} 
    ESG rating demonstrate {'outstanding' if esg_data['rating'] == 'Excellent' else 'good' if esg_data['rating'] == 'Good' else 'moderate' if esg_data['rating'] == 'Average' else 'limited'} 
    commitment to environmental, social, and governance practices.
    """)

# Buy/Sell functionality
st.header("Trade This Stock")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Buy Shares")
    
    current_price = stock_data['Close'].iloc[-1] if not stock_data.empty else 0
    
    shares_to_buy = st.number_input(
        "Number of shares to buy",
        min_value=0,
        max_value=1000,
        value=0,
        step=1,
        key="buy_shares"
    )
    
    total_cost = shares_to_buy * current_price
    st.write(f"Total Cost: ${total_cost:.2f}")
    
    # Display available cash
    st.write(f"Available Cash: ${st.session_state.cash_balance:.2f}")
    
    if st.button("Buy Shares"):
        if total_cost > st.session_state.cash_balance:
            st.error("Insufficient funds for this purchase.")
        elif shares_to_buy <= 0:
            st.error("Please enter a valid number of shares.")
        else:
            # Update portfolio
            if selected_ticker not in st.session_state.portfolio:
                st.session_state.portfolio[selected_ticker] = {
                    "shares": 0,
                    "cost_basis": 0,
                    "current_value": 0
                }
            
            # Add shares to portfolio
            st.session_state.portfolio[selected_ticker]["shares"] += shares_to_buy
            st.session_state.portfolio[selected_ticker]["cost_basis"] += total_cost
            st.session_state.portfolio[selected_ticker]["current_value"] = st.session_state.portfolio[selected_ticker]["shares"] * current_price
            
            # Deduct from cash balance
            st.session_state.cash_balance -= total_cost
            
            # Add to transaction history
            st.session_state.transaction_history.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ticker": selected_ticker,
                "type": "BUY",
                "shares": shares_to_buy,
                "price": current_price,
                "total": total_cost
            })
            
            st.success(f"Successfully purchased {shares_to_buy} shares of {selected_ticker} for ${total_cost:.2f}")
            st.rerun()

with col2:
    st.subheader("Sell Shares")
    
    # Check if user owns this stock
    owned_shares = 0
    if selected_ticker in st.session_state.portfolio:
        owned_shares = st.session_state.portfolio[selected_ticker]["shares"]
    
    st.write(f"You currently own {owned_shares} shares.")
    
    shares_to_sell = st.number_input(
        "Number of shares to sell",
        min_value=0,
        max_value=owned_shares,
        value=0,
        step=1,
        key="sell_shares"
    )
    
    total_value = shares_to_sell * current_price
    st.write(f"Total Value: ${total_value:.2f}")
    
    if st.button("Sell Shares"):
        if shares_to_sell <= 0:
            st.error("Please enter a valid number of shares.")
        elif shares_to_sell > owned_shares:
            st.error("You cannot sell more shares than you own.")
        else:
            # Update portfolio
            st.session_state.portfolio[selected_ticker]["shares"] -= shares_to_sell
            
            # Calculate average cost per share for proper cost basis reduction
            avg_cost = st.session_state.portfolio[selected_ticker]["cost_basis"] / (st.session_state.portfolio[selected_ticker]["shares"] + shares_to_sell)
            cost_reduction = avg_cost * shares_to_sell
            
            st.session_state.portfolio[selected_ticker]["cost_basis"] -= cost_reduction
            st.session_state.portfolio[selected_ticker]["current_value"] = st.session_state.portfolio[selected_ticker]["shares"] * current_price
            
            # If no shares left, remove from portfolio
            if st.session_state.portfolio[selected_ticker]["shares"] == 0:
                del st.session_state.portfolio[selected_ticker]
            
            # Add to cash balance
            st.session_state.cash_balance += total_value
            
            # Add to transaction history
            st.session_state.transaction_history.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ticker": selected_ticker,
                "type": "SELL",
                "shares": shares_to_sell,
                "price": current_price,
                "total": total_value
            })
            
            st.success(f"Successfully sold {shares_to_sell} shares of {selected_ticker} for ${total_value:.2f}")
            st.rerun()

# Historical Performance
st.header("Historical Performance")

# Get historical data
hist_data = get_stock_data(selected_ticker, period="1y")

if not hist_data.empty:
    # Calculate monthly returns
    monthly_returns = hist_data['Close'].resample('M').last().pct_change() * 100
    
    # Create bar chart of monthly returns
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=monthly_returns.index,
            y=monthly_returns.values,
            marker=dict(
                color=['red' if x < 0 else 'green' for x in monthly_returns.values]
            )
        )
    )
    
    fig.update_layout(
        title="Monthly Returns (%)",
        xaxis_title="Month",
        yaxis_title="Return (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key statistics
    col1, col2, col3 = st.columns(3)
    
    # Calculate daily returns
    daily_returns = hist_data['Close'].pct_change() * 100
    
    with col1:
        st.metric(
            "Average Daily Return",
            f"{daily_returns.mean():.2f}%",
            None
        )
    
    with col2:
        st.metric(
            "Volatility (Daily)",
            f"{daily_returns.std():.2f}%",
            None
        )
    
    with col3:
        # Calculate YTD return
        start_of_year = datetime(datetime.now().year, 1, 1)
        ytd_data = hist_data[hist_data.index >= start_of_year]
        
        if not ytd_data.empty:
            ytd_return = ((ytd_data['Close'].iloc[-1] / ytd_data['Close'].iloc[0]) - 1) * 100
            st.metric(
                "YTD Return",
                f"{ytd_return:.2f}%",
                None
            )
        else:
            st.metric(
                "YTD Return",
                "N/A",
                None
            )
else:
    st.info("Could not load historical performance data.")

# News and Updates
st.header("Recent News")

# In a real application, this would fetch actual news about the company
# For now, display a static message
st.info("This section would display recent news and updates about the company.")

# Footer
st.markdown("---")
st.caption(f"Green Energy Stock Exchange Platform | {company_name} ({selected_ticker}) Company Details")
