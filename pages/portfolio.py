"""
Portfolio page for the Green Energy Stock Exchange Platform.
This page is automatically loaded by Streamlit's multi-page app feature.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf

from utils import (
    get_stock_data, 
    get_stock_info,
    format_large_number,
    calculate_portfolio_metrics
)
from config import GREEN_ENERGY_STOCKS, DEFAULT_PORTFOLIO_BALANCE

# Page configuration
st.set_page_config(
    page_title="Portfolio | Green Energy Stock Exchange",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for portfolio if not exists
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = DEFAULT_PORTFOLIO_BALANCE

if 'transaction_history' not in st.session_state:
    st.session_state.transaction_history = []

# Portfolio Page
st.title("Your Green Energy Portfolio")

# Portfolio Overview
st.header("Portfolio Overview")

col1, col2, col3, col4 = st.columns(4)

# Calculate portfolio metrics
if st.session_state.portfolio:
    metrics = calculate_portfolio_metrics(st.session_state.portfolio)
    total_value = metrics["total_value"]
    total_investments = metrics["total_cost"]
else:
    total_value = 0
    total_investments = 0
    metrics = {"total_gain_loss": 0, "percent_gain_loss": 0, "sector_allocation": {}}

with col1:
    st.metric(
        "Total Portfolio Value",
        format_large_number(total_value + st.session_state.cash_balance),
        None
    )

with col2:
    st.metric(
        "Invested Amount",
        format_large_number(total_investments),
        None
    )

with col3:
    st.metric(
        "Cash Balance",
        format_large_number(st.session_state.cash_balance),
        None
    )

with col4:
    st.metric(
        "Total Gain/Loss",
        format_large_number(metrics["total_gain_loss"]),
        f"{metrics['percent_gain_loss']:.2f}%"
    )

# Holdings breakdown
st.subheader("Current Holdings")

if st.session_state.portfolio:
    holdings_data = []
    
    for ticker, holding in st.session_state.portfolio.items():
        # Get current price
        stock_data = get_stock_data(ticker, period="1d")
        current_price = stock_data['Close'].iloc[-1] if not stock_data.empty else 0
        
        # Find company name
        company_name = ""
        for t, name, sector in GREEN_ENERGY_STOCKS:
            if t == ticker:
                company_name = name
                break
        
        # Calculate values
        current_value = holding["shares"] * current_price
        cost_basis = holding["cost_basis"]
        gain_loss = current_value - cost_basis
        gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        # Update current value in portfolio
        st.session_state.portfolio[ticker]["current_value"] = current_value
        
        holdings_data.append({
            "Ticker": ticker,
            "Company": company_name,
            "Shares": holding["shares"],
            "Current Price": current_price,
            "Market Value": current_value,
            "Cost Basis": cost_basis,
            "Gain/Loss": gain_loss,
            "Gain/Loss %": gain_loss_percent
        })
    
    if holdings_data:
        holdings_df = pd.DataFrame(holdings_data)
        
        st.dataframe(
            holdings_df,
            column_config={
                "Current Price": st.column_config.NumberColumn(
                    "Current Price",
                    format="$%.2f"
                ),
                "Market Value": st.column_config.NumberColumn(
                    "Market Value",
                    format="$%.2f"
                ),
                "Cost Basis": st.column_config.NumberColumn(
                    "Cost Basis",
                    format="$%.2f"
                ),
                "Gain/Loss": st.column_config.NumberColumn(
                    "Gain/Loss",
                    format="$%.2f"
                ),
                "Gain/Loss %": st.column_config.NumberColumn(
                    "Gain/Loss %",
                    format="%.2f%%"
                ),
            },
            use_container_width=True
        )
    else:
        st.info("No holdings in your portfolio.")
else:
    st.info("Your portfolio is empty. Visit company details to buy stocks.")

# Portfolio Allocation
if st.session_state.portfolio:
    st.subheader("Portfolio Allocation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sector allocation chart
        if metrics["sector_allocation"]:
            sector_data = pd.DataFrame({
                "Sector": metrics["sector_allocation"].keys(),
                "Allocation": metrics["sector_allocation"].values()
            })
            
            fig = px.pie(
                sector_data,
                values="Allocation",
                names="Sector",
                title="Sector Allocation"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sector allocation data not available.")
    
    with col2:
        # Stock allocation chart
        stock_values = []
        for ticker, holding in st.session_state.portfolio.items():
            company_name = ""
            for t, name, _ in GREEN_ENERGY_STOCKS:
                if t == ticker:
                    company_name = name
                    break
            
            stock_values.append({
                "Stock": f"{company_name} ({ticker})",
                "Value": holding["current_value"]
            })
        
        if stock_values:
            stock_df = pd.DataFrame(stock_values)
            fig = px.pie(
                stock_df,
                values="Value",
                names="Stock",
                title="Stock Allocation"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Stock allocation data not available.")

# Performance over time
if st.session_state.portfolio and st.session_state.transaction_history:
    st.subheader("Performance Tracking")
    
    # Calculate daily portfolio values (simplified version)
    # In a real app, we would track daily values more accurately
    
    # Get the earliest transaction date
    transaction_dates = [datetime.strptime(t["date"], "%Y-%m-%d %H:%M:%S") 
                         for t in st.session_state.transaction_history]
    if transaction_dates:
        start_date = min(transaction_dates).date()
        end_date = datetime.now().date()
        
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create a performance tracking dataframe (simplified)
        # This is a simplified approach that doesn't account for all historical transactions
        # In a real app, this would be more complex and accurate
        performance_data = []
        for current_date in date_range:
            # Calculate portfolio value as of this date
            # Note: This is simplified and doesn't account for historical prices or holdings
            # A real implementation would track accurate daily values
            
            # For now, just add current portfolio value
            if current_date.date() == datetime.now().date():
                performance_data.append({
                    "Date": current_date,
                    "Value": total_value + st.session_state.cash_balance
                })
            else:
                # Simulate some historical values
                day_diff = (end_date - current_date.date()).days
                value_factor = 1 - (day_diff * 0.002)  # Simple decay factor
                performance_data.append({
                    "Date": current_date,
                    "Value": (total_value + st.session_state.cash_balance) * value_factor
                })
        
        perf_df = pd.DataFrame(performance_data)
        
        # Plot portfolio value over time
        fig = px.line(
            perf_df,
            x="Date",
            y="Value",
            title="Portfolio Value Over Time"
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            yaxis_tickformat="$,.2f",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a disclaimer
        st.caption("Note: Historical performance is simulated for demonstration purposes.")

# Transaction History
st.header("Transaction History")

if st.session_state.transaction_history:
    transactions_df = pd.DataFrame(st.session_state.transaction_history)
    
    st.dataframe(
        transactions_df,
        column_config={
            "date": st.column_config.DatetimeColumn(
                "Date",
                format="YYYY-MM-DD HH:mm"
            ),
            "price": st.column_config.NumberColumn(
                "Price",
                format="$%.2f"
            ),
            "total": st.column_config.NumberColumn(
                "Total",
                format="$%.2f"
            ),
        },
        use_container_width=True
    )
else:
    st.info("No transaction history yet.")

# Portfolio management
st.header("Portfolio Management")

# Add funds option
col1, col2 = st.columns(2)

with col1:
    st.subheader("Add Funds")
    amount_to_add = st.number_input(
        "Amount to add ($)",
        min_value=0.0,
        value=0.0,
        step=1000.0
    )
    
    if st.button("Add Funds"):
        if amount_to_add > 0:
            st.session_state.cash_balance += amount_to_add
            st.success(f"Successfully added ${amount_to_add:.2f} to your account.")
            st.rerun()
        else:
            st.error("Please enter a valid amount to add.")

with col2:
    st.subheader("Reset Portfolio")
    
    if st.button("Reset Portfolio to Initial State"):
        st.session_state.portfolio = {}
        st.session_state.cash_balance = DEFAULT_PORTFOLIO_BALANCE
        st.session_state.transaction_history = []
        st.success("Portfolio has been reset to initial state.")
        st.rerun()

# Footer
st.markdown("---")
st.caption("Green Energy Stock Exchange Platform | Portfolio Management")
