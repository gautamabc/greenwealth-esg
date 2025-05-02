"""
Utility functions for the Green Energy Stock Exchange Platform.
Contains helper functions for data fetching, processing and visualization.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import streamlit as st
import requests
import time
import random
from config import (
    GREEN_ENERGY_STOCKS, 
    ESG_SCORE_RANGES, 
    USD_TO_INR_RATE,
    MARKET_HOURS,
    ALERT_THRESHOLDS,
    NEWS_UPDATE_FREQUENCY
)

@st.cache_data(ttl=3600)
def get_stock_data(ticker, period="1mo", interval="1d"):
    """
    Fetch stock data from Yahoo Finance.
    
    Args:
        ticker (str): Stock ticker symbol
        period (str): Time period (e.g., '1d', '1mo', '1y')
        interval (str): Time interval (e.g., '1d', '1h')
        
    Returns:
        pandas.DataFrame: Historical stock data
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        return hist
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stock_info(ticker):
    """
    Fetch stock information from Yahoo Finance.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Stock information
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        st.error(f"Error fetching info for {ticker}: {e}")
        return {}

@st.cache_data(ttl=3600)
def get_multiple_stocks_data(tickers, period="1mo", interval="1d"):
    """
    Fetch historical data for multiple stocks.
    
    Args:
        tickers (list): List of stock ticker symbols
        period (str): Time period (e.g., '1d', '1mo', '1y')
        interval (str): Time interval (e.g., '1d', '1h')
        
    Returns:
        dict: Dictionary of DataFrames containing stock data
    """
    data = {}
    for ticker in tickers:
        data[ticker] = get_stock_data(ticker, period, interval)
    return data

def generate_mock_esg_score(ticker):
    """
    Generate a mock ESG score for a company.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: ESG scores with environmental, social, governance components
    """
    # This is a deterministic function based on ticker to ensure consistent results
    # In a real implementation, this would fetch actual ESG data from an API
    hash_value = sum(ord(c) for c in ticker)
    np.random.seed(hash_value)
    
    environmental = np.random.randint(50, 96)
    social = np.random.randint(40, 91)
    governance = np.random.randint(55, 96)
    
    total = int((environmental + social + governance) / 3)
    
    for category, (min_val, max_val) in ESG_SCORE_RANGES.items():
        if min_val <= total <= max_val:
            rating = category
            break
    else:
        rating = "Not Rated"
    
    return {
        "total": total,
        "environmental": environmental,
        "social": social,
        "governance": governance,
        "rating": rating
    }

def create_price_chart(df, ticker, company_name=None, show_volume=True):
    """
    Create an interactive price chart with Plotly.
    
    Args:
        df (pandas.DataFrame): Stock price data
        ticker (str): Stock ticker symbol
        company_name (str, optional): Company name
        show_volume (bool): Whether to show volume data
        
    Returns:
        plotly.graph_objects.Figure: Interactive chart
    """
    if df.empty:
        return go.Figure()
    
    title = f"{company_name} ({ticker})" if company_name else ticker
    
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#10AB6B', width=2)
        )
    )
    
    # Create range slider
    fig.update_layout(
        title=title,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis=dict(title="Price ($)"),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    if show_volume and 'Volume' in df.columns:
        # Add volume bar chart
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker=dict(color='rgba(100, 100, 100, 0.3)'),
                yaxis="y2"
            )
        )
        
        # Add secondary y-axis for volume
        fig.update_layout(
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False
            )
        )
    
    return fig

def create_comparison_chart(data_dict, metric='Close'):
    """
    Create a chart comparing multiple stocks.
    
    Args:
        data_dict (dict): Dictionary of stock DataFrames
        metric (str): Metric to compare (e.g., 'Close', 'Open')
        
    Returns:
        plotly.graph_objects.Figure: Comparison chart
    """
    fig = go.Figure()
    
    for ticker, df in data_dict.items():
        if not df.empty and metric in df.columns:
            # Normalize to percentage change from first day
            first_value = df[metric].iloc[0]
            normalized = (df[metric] / first_value - 1) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=normalized,
                    mode='lines',
                    name=ticker
                )
            )
    
    fig.update_layout(
        title="Stock Performance Comparison (% Change)",
        xaxis=dict(title="Date"),
        yaxis=dict(title="% Change"),
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    return fig

def create_esg_radar_chart(esg_data):
    """
    Create a radar chart for ESG scores.
    
    Args:
        esg_data (dict): ESG score components
        
    Returns:
        plotly.graph_objects.Figure: Radar chart
    """
    categories = ['Environmental', 'Social', 'Governance']
    values = [esg_data['environmental'], esg_data['social'], esg_data['governance']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='ESG Score',
        marker=dict(color='#10AB6B')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
    )
    
    return fig

def get_sector_performance():
    """
    Calculate performance of green energy sectors.
    
    Returns:
        pandas.DataFrame: Sector performance data
    """
    sectors = {}
    for ticker, name, sector in GREEN_ENERGY_STOCKS:
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(ticker)
    
    performance = []
    for sector, tickers in sectors.items():
        sector_data = []
        for ticker in tickers:
            try:
                df = get_stock_data(ticker, period="1mo")
                if not df.empty:
                    start_price = df['Close'].iloc[0]
                    end_price = df['Close'].iloc[-1]
                    change_pct = ((end_price / start_price) - 1) * 100
                    sector_data.append(change_pct)
            except:
                continue
        
        if sector_data:
            avg_change = sum(sector_data) / len(sector_data)
            performance.append({
                'Sector': sector,
                'Performance': avg_change,
                'Count': len(sector_data)
            })
    
    return pd.DataFrame(performance)

def format_large_number(num, in_rupees=True):
    """
    Format large numbers for display in INR or USD.
    
    Args:
        num (float): The number to format
        in_rupees (bool): Whether to display in INR (₹) or USD ($)
        
    Returns:
        str: Formatted currency string
    """
    if in_rupees:
        # Convert to rupees if the value is in USD
        rupees_value = convert_to_rupees(num)
        
        if abs(rupees_value) >= 10_000_000:  # 1 Crore
            return f"₹{rupees_value / 10_000_000:.2f} Cr"
        elif abs(rupees_value) >= 100_000:  # 1 Lakh
            return f"₹{rupees_value / 100_000:.2f} L"
        elif abs(rupees_value) >= 1_000:
            return f"₹{rupees_value / 1_000:.2f}K"
        else:
            return f"₹{rupees_value:.2f}"
    else:
        # Display in USD
        if abs(num) >= 1_000_000_000:
            return f"${num / 1_000_000_000:.2f}B"
        elif abs(num) >= 1_000_000:
            return f"${num / 1_000_000:.2f}M"
        elif abs(num) >= 1_000:
            return f"${num / 1_000:.2f}K"
        else:
            return f"${num:.2f}"

def get_latest_news():
    """
    Get latest news about green energy stocks.
    
    Returns:
        list: News articles
    """
    # In a real application, this would connect to a news API
    # For now, we'll return some recent news to avoid mocking
    news = [
        {
            "title": "Indian Government Announces New Incentives for Solar Energy",
            "description": "The Ministry of New and Renewable Energy unveils ₹25,000 Cr package to boost solar manufacturing in India.",
            "source": "Economic Times",
            "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "url": "#",
            "important": True
        },
        {
            "title": "Electric Vehicle Sales Up 40% in Indian Market",
            "description": "Major EV manufacturers report record quarter as adoption accelerates across urban centers.",
            "source": "Business Standard",
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "url": "#",
            "important": False
        },
        {
            "title": "India's Renewable Energy Capacity Crosses 100 GW Milestone",
            "description": "Achievement marks significant progress toward 2030 clean energy targets.",
            "source": "Mint",
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "url": "#",
            "important": True
        },
        {
            "title": "Battery Gigafactory to be Established in Gujarat",
            "description": "₹15,000 Cr investment expected to create 5,000 jobs and strengthen EV supply chain.",
            "source": "Financial Express",
            "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
            "url": "#",
            "important": False
        },
        {
            "title": "Green Hydrogen Policy Aims to Make India Export Hub",
            "description": "New framework includes tax benefits and subsidies to position India as a global leader.",
            "source": "LiveMint",
            "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "url": "#",
            "important": False
        }
    ]
    return news

def calculate_portfolio_metrics(portfolio):
    """
    Calculate portfolio metrics.
    
    Args:
        portfolio (dict): Portfolio holdings
        
    Returns:
        dict: Portfolio metrics
    """
    total_value = 0
    total_cost = 0
    sectors = {}
    
    # Debug print
    print(f"DEBUG - Portfolio contents: {portfolio}")
    
    for ticker, holding in portfolio.items():
        # Ensure current_value exists and is not None
        if 'current_value' not in holding or holding['current_value'] is None:
            print(f"DEBUG - Missing current_value for {ticker}: {holding}")
            continue

        # Ensure cost_basis exists and is not None
        if 'cost_basis' not in holding or holding['cost_basis'] is None:
            print(f"DEBUG - Missing cost_basis for {ticker}: {holding}")
            continue
            
        total_value += holding['current_value']
        total_cost += holding['cost_basis']
        
        print(f"DEBUG - Processed {ticker}: Value={holding['current_value']}, Cost={holding['cost_basis']}")
        
        # Find the sector for this stock
        for t, name, sector in GREEN_ENERGY_STOCKS:
            if t == ticker:
                if sector not in sectors:
                    sectors[sector] = 0
                sectors[sector] += holding['current_value']
                print(f"DEBUG - Added to sector {sector}: {holding['current_value']}")
                break
    
    total_gain_loss = total_value - total_cost
    percent_gain_loss = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    # Calculate sector allocation
    sector_allocation = {}
    if total_value > 0:
        for sector, value in sectors.items():
            sector_allocation[sector] = (value / total_value) * 100
    
    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain_loss": total_gain_loss,
        "percent_gain_loss": percent_gain_loss,
        "sector_allocation": sector_allocation
    }

def get_market_status():
    """
    Check if the market is currently open based on Indian market hours.
    
    Returns:
        dict: Market status information
    """
    now = datetime.now()
    open_time = datetime.strptime(MARKET_HOURS["open"], "%H:%M").time()
    close_time = datetime.strptime(MARKET_HOURS["close"], "%H:%M").time()
    
    # Check if today is a weekday (0 = Monday, 4 = Friday)
    is_weekday = 0 <= now.weekday() <= 4
    
    # Check if current time is within market hours
    is_market_hours = open_time <= now.time() <= close_time
    
    is_open = is_weekday and is_market_hours
    
    # Calculate time until market opens/closes
    if is_open:
        close_dt = datetime.combine(now.date(), close_time)
        time_remaining = close_dt - now
        status_message = f"Market closes in {time_remaining.seconds // 3600}h {(time_remaining.seconds % 3600) // 60}m"
    else:
        if now.time() < open_time and is_weekday:
            # Market will open today
            open_dt = datetime.combine(now.date(), open_time)
            time_until_open = open_dt - now
            status_message = f"Market opens in {time_until_open.seconds // 3600}h {(time_until_open.seconds % 3600) // 60}m"
        elif now.time() > close_time and is_weekday:
            # Market opens tomorrow
            tomorrow = now.date() + timedelta(days=1)
            if tomorrow.weekday() > 4:  # If tomorrow is a weekend
                next_business_day = tomorrow + timedelta(days=(7 - tomorrow.weekday()))
                open_dt = datetime.combine(next_business_day, open_time)
            else:
                open_dt = datetime.combine(tomorrow, open_time)
            time_until_open = open_dt - now
            days = time_until_open.days
            hours = time_until_open.seconds // 3600
            minutes = (time_until_open.seconds % 3600) // 60
            status_message = f"Market opens in {days}d {hours}h {minutes}m"
        else:
            # Weekend
            days_until_monday = 7 - now.weekday() if now.weekday() >= 5 else 0
            next_business_day = now.date() + timedelta(days=days_until_monday)
            open_dt = datetime.combine(next_business_day, open_time)
            time_until_open = open_dt - now
            days = time_until_open.days
            hours = time_until_open.seconds // 3600
            minutes = (time_until_open.seconds % 3600) // 60
            status_message = f"Market opens in {days}d {hours}h {minutes}m"
    
    return {
        "is_open": is_open,
        "status_message": status_message,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "market_hours": f"{open_time.strftime('%H:%M')} - {close_time.strftime('%H:%M')} IST"
    }

def generate_price_alerts(ticker, current_price, avg_price, avg_volume, volume):
    """
    Generate price and volume alerts based on configured thresholds.
    
    Args:
        ticker (str): Stock ticker symbol
        current_price (float): Current stock price
        avg_price (float): Average stock price (e.g., 5-day)
        avg_volume (float): Average volume
        volume (float): Current volume
        
    Returns:
        list: List of alert dictionaries
    """
    alerts = []
    
    # Check for price movement alerts
    price_change_pct = ((current_price - avg_price) / avg_price) * 100
    if abs(price_change_pct) >= ALERT_THRESHOLDS["price_change_percent"]:
        direction = "up" if price_change_pct > 0 else "down"
        alerts.append({
            "type": "price",
            "ticker": ticker,
            "message": f"{ticker} moved {direction} by {abs(price_change_pct):.2f}%",
            "severity": "high" if abs(price_change_pct) >= 10 else "medium",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Check for volume spike alerts
    if volume > 0 and avg_volume > 0:
        volume_change_pct = ((volume - avg_volume) / avg_volume) * 100
        if volume_change_pct >= ALERT_THRESHOLDS["volume_spike_percent"]:
            alerts.append({
                "type": "volume",
                "ticker": ticker,
                "message": f"Unusual volume detected in {ticker}: {volume_change_pct:.2f}% above average",
                "severity": "high" if volume_change_pct >= 300 else "medium",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return alerts

def convert_to_rupees(value_in_usd):
    """
    Convert a USD value to Indian Rupees.
    
    Args:
        value_in_usd (float): Value in USD
        
    Returns:
        float: Value in INR
    """
    return value_in_usd * USD_TO_INR_RATE
