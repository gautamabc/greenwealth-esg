"""
GreenWealth Investment Platform
A professional Streamlit-based financial platform for green energy stocks with
interactive visualization, portfolio tracking, real-time data, and ESG insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
import time
from streamlit_option_menu import option_menu

from utils import (
    get_stock_data, 
    get_stock_info, 
    get_multiple_stocks_data,
    generate_mock_esg_score,
    create_price_chart,
    create_comparison_chart,
    create_esg_radar_chart,
    get_sector_performance,
    format_large_number,
    get_latest_news,
    calculate_portfolio_metrics,
    get_market_status,
    generate_price_alerts,
    convert_to_rupees
)
from config import (
    GREEN_ENERGY_STOCKS, 
    TIME_PERIODS, 
    DEFAULT_PORTFOLIO_BALANCE,
    USD_TO_INR_RATE,
    MARKET_HOURS,
    ALERT_THRESHOLDS
)

# Page configuration
st.set_page_config(
    page_title="GreenWealth Investment Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "1mo"
    
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "FSLR"
    
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}
    
if "cash_balance" not in st.session_state:
    st.session_state.cash_balance = DEFAULT_PORTFOLIO_BALANCE
    
if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []
    
if "currency" not in st.session_state:
    st.session_state.currency = "INR (₹)"
    
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
    
if 'username' not in st.session_state:
    st.session_state.username = ""
    
if 'payment_methods' not in st.session_state:
    st.session_state.payment_methods = []
    
if 'payment_history' not in st.session_state:
    st.session_state.payment_history = []
    
# Default page selection (will be overridden by navbar selection if user is logged in)
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Dashboard"

# Custom CSS for professional look
st.markdown("""
<style>
    /* Custom styling */
    .main-header {
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    .sub-header {
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.8rem !important;
    }
    
    .stButton>button {
        color: white;
        background-color: #16B174;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #0D8A59;
    }
    
    /* Card styling */
    .card {
        background-color: #1E2127;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Navigation Bar */
    .navbar {
        padding: 1rem 0;
        background-color: #1E2127;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Login Form */
    .login-form {
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
        background-color: #1E2127;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Data labels */
    .data-label {
        font-weight: bold;
        color: #16B174;
    }
    
    /* Status indicator */
    .status-indicator {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    
    .status-open {
        background-color: #16B174;
    }
    
    .status-closed {
        background-color: #FF4B4B;
    }
    
    /* Custom tabs styling */
    .custom-tab {
        background-color: #1E2127;
        padding: 10px 15px;
        border-radius: 5px 5px 0 0;
        margin-right: 5px;
        cursor: pointer;
    }
    
    .custom-tab-active {
        background-color: #16B174;
        color: white;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #1E2127;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #16B174;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #9FA2A7;
    }
</style>
""", unsafe_allow_html=True)

# Login/Sign Up functionality
def show_login_page():
    st.markdown("<h1 class='main-header'>Welcome to GreenWealth Investment Platform</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <h2>The Future of Green Energy Investing</h2>
            <p>Invest in a sustainable future with our specialized green energy investment platform. 
            Get real-time data, ESG insights, and professional trading tools.</p>
            <ul>
                <li>Exclusive focus on green energy stocks</li>
                <li>Advanced ESG scoring and analysis</li>
                <li>Real-time market data from global exchanges</li>
                <li>Secure payment gateway for instant funding</li>
                <li>Comprehensive portfolio management tools</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Featured stocks showcase
        st.markdown("<h3>Featured Green Energy Companies</h3>", unsafe_allow_html=True)
        featured_cols = st.columns(3)
        
        featured_stocks = [
            {"ticker": "FSLR", "name": "First Solar", "sector": "Solar Energy"},
            {"ticker": "TSLA", "name": "Tesla", "sector": "Electric Vehicles"},
            {"ticker": "NEE", "name": "NextEra Energy", "sector": "Renewable Energy"}
        ]
        
        for i, stock in enumerate(featured_stocks):
            with featured_cols[i]:
                stock_data = get_stock_data(stock["ticker"], period="5d")
                if not stock_data.empty:
                    current_price = stock_data['Close'].iloc[-1]
                    prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
                    change_pct = ((current_price / prev_price) - 1) * 100
                    
                    # Format with INR by default
                    price_display = format_large_number(current_price, in_rupees=True)
                    
                    color = "green" if change_pct >= 0 else "red"
                    st.markdown(f"""
                    <div class="metric-container">
                        <div>{stock['name']} ({stock['ticker']})</div>
                        <div class="metric-value">{price_display}</div>
                        <div style="color: {color};">{change_pct:.2f}%</div>
                        <div class="metric-label">{stock['sector']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-container">
                        <div>{stock['name']} ({stock['ticker']})</div>
                        <div class="metric-value">Loading...</div>
                        <div class="metric-label">{stock['sector']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='login-form'>", unsafe_allow_html=True)
        st.markdown("<h3>Login to Your Account</h3>", unsafe_allow_html=True)
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Login"):
                if username and password:  # Simple validation
                    st.session_state.user_logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Please enter both username and password")
        
        with col2:
            if st.button("Sign Up"):
                if username and password:  # Simple validation
                    st.session_state.user_logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Please enter both username and password")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Market status indicator in login page
        market_status = get_market_status()
        status_color = "#16B174" if market_status["is_open"] else "#FF4B4B"
        
        st.markdown(f"""
        <div style="background-color: #1E2127; padding: 15px; border-radius: 10px; margin-top: 20px;">
            <div style="font-weight: bold; margin-bottom: 10px;">Market Status</div>
            <div style="display: flex; align-items: center;">
                <div style="height: 12px; width: 12px; border-radius: 50%; background-color: {status_color}; margin-right: 8px;"></div>
                <span>{market_status["status_message"]}</span>
            </div>
            <div style="font-size: 0.8em; margin-top: 5px; color: #9FA2A7;">Market hours: {market_status["market_hours"]}</div>
        </div>
        """, unsafe_allow_html=True)

# Navigation bar for logged-in user
def show_navbar():
    # Custom navbar
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Portfolio", "Market Analysis", "Companies", "Payments", "Account"],
        icons=["house", "pie-chart", "graph-up", "building", "credit-card", "person"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0px", "background-color": "#1E2127", "border-radius": "10px", "margin-bottom": "20px"},
            "icon": {"color": "#9FA2A7", "font-size": "14px"},
            "nav-link": {"font-size": "14px", "text-align": "center", "padding": "10px", "margin": "0px", "border-radius": "5px"},
            "nav-link-selected": {"background-color": "#16B174"},
        }
    )
    
    # Market status indicator with better styling
    market_status = get_market_status()
    status_color = "#16B174" if market_status["is_open"] else "#FF4B4B"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="background-color: #1E2127; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; justify-content: center;">
                <div style="height: 10px; width: 10px; border-radius: 50%; background-color: {status_color}; margin-right: 8px;"></div>
                <span style="font-weight: bold;">{market_status["status_message"]}</span>
                <span style="margin-left: 15px; font-size: 0.9em; color: #9FA2A7;">Market hours: {market_status["market_hours"]}</span>
                <span style="margin-left: 15px; font-size: 0.9em;">User: <b>{st.session_state.username}</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return selected

# Currency selector component
def currency_selector():
    currency_options = ["INR (₹)", "USD ($)"]
    
    col1, col2 = st.columns([3, 1])
    with col2:
        selected_currency = st.selectbox(
            "Display Currency",
            currency_options,
            index=currency_options.index(st.session_state.currency)
        )
        
        if selected_currency != st.session_state.currency:
            st.session_state.currency = selected_currency
            st.rerun()

# Main application flow
if not st.session_state.user_logged_in:
    show_login_page()
else:
    # Navbar
    st.session_state.selected_page = show_navbar()
    
    # Currency selector
    currency_selector()
    
    # Pages
    if st.session_state.selected_page == "Dashboard":
        st.markdown("<h1 class='main-header'>GreenWealth Investment Dashboard</h1>", unsafe_allow_html=True)
        
        # Market Overview
        st.markdown("<h2 class='sub-header'>Market Overview</h2>", unsafe_allow_html=True)
        
        # Top metrics row
        col1, col2, col3 = st.columns(3)
        
        # Get some key green energy stocks for metrics
        key_stocks = ["FSLR", "ENPH", "NEE", "TSLA"]
        market_data = {}
        
        for ticker in key_stocks:
            stock_data = get_stock_data(ticker, period="5d")
            if not stock_data.empty:
                latest = stock_data.iloc[-1]
                previous = stock_data.iloc[-2] if len(stock_data) > 1 else latest
                change = (latest['Close'] - previous['Close']) / previous['Close'] * 100
                market_data[ticker] = {
                    "price": latest['Close'],
                    "change": change
                }
        
        # Display metrics
        in_rupees = "INR" in st.session_state.currency
        
        with col1:
            if "FSLR" in market_data:
                price_display = format_large_number(market_data['FSLR']['price'], in_rupees=in_rupees)
                st.metric(
                    "First Solar (FSLR)",
                    price_display,
                    f"{market_data['FSLR']['change']:.2f}%"
                )
            else:
                st.metric("First Solar (FSLR)", "Loading...", "0.00%")
                
            if "TSLA" in market_data:
                price_display = format_large_number(market_data['TSLA']['price'], in_rupees=in_rupees)
                st.metric(
                    "Tesla (TSLA)",
                    price_display,
                    f"{market_data['TSLA']['change']:.2f}%"
                )
            else:
                st.metric("Tesla (TSLA)", "Loading...", "0.00%")
        
        with col2:
            if "ENPH" in market_data:
                price_display = format_large_number(market_data['ENPH']['price'], in_rupees=in_rupees)
                st.metric(
                    "Enphase Energy (ENPH)",
                    price_display,
                    f"{market_data['ENPH']['change']:.2f}%"
                )
            else:
                st.metric("Enphase Energy (ENPH)", "Loading...", "0.00%")
                
            # Get sector performance
            sector_perf = get_sector_performance()
            if not sector_perf.empty:
                best_sector = sector_perf.iloc[sector_perf['Performance'].argmax()]
                st.metric(
                    f"Best Sector: {best_sector['Sector']}",
                    f"{best_sector['Performance']:.2f}%",
                    f"{best_sector['Count']} stocks"
                )
            else:
                st.metric("Best Sector", "Loading...", "0.00%")
        
        with col3:
            if "NEE" in market_data:
                price_display = format_large_number(market_data['NEE']['price'], in_rupees=in_rupees)
                st.metric(
                    "NextEra Energy (NEE)",
                    price_display,
                    f"{market_data['NEE']['change']:.2f}%"
                )
            else:
                st.metric("NextEra Energy (NEE)", "Loading...", "0.00%")
                
            # Overall green energy sector performance
            if not sector_perf.empty:
                avg_performance = sector_perf['Performance'].mean()
                st.metric(
                    "Green Energy Sector",
                    f"{avg_performance:.2f}%",
                    f"{len(sector_perf)} sub-sectors"
                )
            else:
                st.metric("Green Energy Sector", "Loading...", "0 sub-sectors")
        
        # Sector Performance Chart
        st.subheader("Sector Performance (1 Month)")
        
        if not sector_perf.empty:
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
        else:
            st.info("Loading sector performance data...")
        
        # Top performing stocks
        st.subheader("Top Performing Green Energy Stocks")
        
        # Get performance data for all stocks
        performance_data = []
        for ticker, name, sector in GREEN_ENERGY_STOCKS:
            stock_data = get_stock_data(ticker, period="1mo")
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
            performance_df = performance_df.sort_values("Performance", ascending=False)
            
            # Show top performers
            in_rupees = "INR" in st.session_state.currency
            price_format = "₹%.2f" if in_rupees else "$%.2f"
            
            st.dataframe(
                performance_df[["Ticker", "Name", "Sector", "Performance", "Current Price"]].head(10),
                column_config={
                    "Performance": st.column_config.NumberColumn(
                        "1 Month Performance",
                        format="%.2f%%"
                    ),
                    "Current Price": st.column_config.NumberColumn(
                        "Current Price",
                        format=price_format
                    )
                },
                use_container_width=True
            )
        else:
            st.info("Loading performance data...")
        
        # Latest News
        st.header("Latest Green Energy News")
        news = get_latest_news()
        
        for item in news:
            st.markdown(f"**{item['title']}**")
            st.markdown(f"{item['description']}")
            st.caption(f"{item['source']} • {item['date']}")
            st.markdown("---")
        
        # Market Analysis Teaser
        st.header("Market Analysis")
        
        # Get comparison data for key green energy sectors
        col1, col2 = st.columns(2)
        
        with col1:
            # Solar stocks comparison
            solar_tickers = ["FSLR", "ENPH", "SEDG", "RUN", "CSIQ"]
            solar_data = get_multiple_stocks_data(solar_tickers, period="1mo")
            
            if all(not df.empty for df in solar_data.values()):
                st.subheader("Solar Energy Stocks Comparison")
                fig = create_comparison_chart(solar_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Loading solar stocks comparison...")
        
        with col2:
            # EV stocks comparison
            ev_tickers = ["TSLA", "NIO", "RIVN", "LCID"]
            ev_data = get_multiple_stocks_data(ev_tickers, period="1mo")
            
            if all(not df.empty for df in ev_data.values()):
                st.subheader("Electric Vehicle Stocks Comparison")
                fig = create_comparison_chart(ev_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Loading EV stocks comparison...")
        
        # Portfolio overview (if they have one)
        if st.session_state.portfolio:
            st.header("Your Portfolio Overview")
            
            metrics = calculate_portfolio_metrics(st.session_state.portfolio)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Value",
                    format_large_number(metrics["total_value"]),
                    f"{metrics['percent_gain_loss']:.2f}%"
                )
            
            with col2:
                st.metric(
                    "Cash Balance",
                    format_large_number(st.session_state.cash_balance),
                    None
                )
            
            with col3:
                st.metric(
                    "Total Gain/Loss",
                    format_large_number(metrics["total_gain_loss"]),
                    None
                )
            
            # Show a teaser button to view full portfolio
            if st.button("View Full Portfolio"):
                # Switch to portfolio page
                st.session_state.selected_page = "Portfolio"
                st.rerun()
        else:
            st.info("You haven't created a portfolio yet. Visit the Portfolio page to get started.")

    elif st.session_state.selected_page == "Companies":
        # Company selector
        st.sidebar.header("Select Company")
        # Create options list with ticker and company name
        ticker_options = [f"{name} ({ticker})" for ticker, name, _ in GREEN_ENERGY_STOCKS]
        
        # Add company selector in sidebar
        selected_company = st.sidebar.selectbox(
            "Choose a green energy company",
            ticker_options,
            index=ticker_options.index(f"First Solar (FSLR)") if "First Solar (FSLR)" in ticker_options else 0
        )
        
        # Extract ticker from selection
        ticker = selected_company.split("(")[1].split(")")[0]
        
        # Update session state
        if st.session_state.selected_ticker != ticker:
            st.session_state.selected_ticker = ticker
        
        # Time period selector
        period_options = list(TIME_PERIODS.keys())
        selected_period = st.sidebar.selectbox(
            "Select Time Period",
            period_options,
            index=period_options.index(st.session_state.selected_period) if st.session_state.selected_period in period_options else 0
        )
        
        if st.session_state.selected_period != selected_period:
            st.session_state.selected_period = selected_period
        
        period = TIME_PERIODS[selected_period]
        
        # Get company info
        info = get_stock_info(ticker)
        company_name = info.get('longName', ticker) if info else ticker
        
        st.title(f"{company_name} ({ticker})")
        
        # Company metadata
        if info:
            col1, col2, col3 = st.columns(3)
            
            in_rupees = "INR" in st.session_state.currency
            
            # Current price with appropriate currency
            curr_price = info.get('currentPrice', 0)
            price_display = format_large_number(curr_price, in_rupees=in_rupees)
            
            with col1:
                st.metric(
                    "Current Price",
                    price_display,
                    f"{info.get('regularMarketChangePercent', 0):.2f}%"
                )
            
            with col2:
                st.metric(
                    "Market Cap",
                    format_large_number(info.get('marketCap', 0), in_rupees=in_rupees),
                    None
                )
        
            # 52 Week Range with appropriate currency
            low_price = info.get('fiftyTwoWeekLow', 0)
            high_price = info.get('fiftyTwoWeekHigh', 0)
            
            if in_rupees:
                range_display = f"₹{low_price:.2f} - ₹{high_price:.2f}"
            else:
                range_display = f"${low_price:.2f} - ${high_price:.2f}"
                
            with col3:
                st.metric(
                    "52 Week Range",
                    range_display,
                    None
                )
        
        # Stock price chart
        st.subheader("Stock Price History")
        stock_data = get_stock_data(ticker, period=period)
        
        if not stock_data.empty:
            fig = create_price_chart(stock_data, ticker, company_name)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Could not load stock data for {ticker}")
        
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
                in_rupees = "INR" in st.session_state.currency
                currency_symbol = "₹" if in_rupees else "$"
                
                with stats_cols[0]:
                    st.metric("P/E Ratio", f"{info.get('trailingPE', 0):.2f}", None)
                    st.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%", None)
                
                with stats_cols[1]:
                    week_high = info.get('fiftyTwoWeekHigh', 0)
                    week_low = info.get('fiftyTwoWeekLow', 0)
                    st.metric("52 Week High", f"{currency_symbol}{week_high:.2f}", None)
                    st.metric("52 Week Low", f"{currency_symbol}{week_low:.2f}", None)
                
                with stats_cols[2]:
                    st.metric("Volume", f"{info.get('volume', 0):,}", None)
                    st.metric("Avg Volume", f"{info.get('averageVolume', 0):,}", None)
        
        with col2:
            st.subheader("ESG Score")
            
            # Get ESG data
            esg_data = generate_mock_esg_score(ticker)
            
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
            in_rupees = "INR" in st.session_state.currency
            currency_symbol = "₹" if in_rupees else "$"
            st.write(f"Total Cost: {currency_symbol}{total_cost:.2f}")
            
            if st.button("Buy Shares"):
                if total_cost > st.session_state.cash_balance:
                    st.error("Insufficient funds for this purchase.")
                elif shares_to_buy <= 0:
                    st.error("Please enter a valid number of shares.")
                else:
                    # Update portfolio with complete initialization
                    if ticker not in st.session_state.portfolio:
                        st.session_state.portfolio[ticker] = {
                            "shares": 0,
                            "cost_basis": 0,
                            "current_value": 0
                        }
                    
                    # Add shares to portfolio with proper calculations
                    st.session_state.portfolio[ticker]["shares"] += shares_to_buy
                    st.session_state.portfolio[ticker]["cost_basis"] += total_cost
                    st.session_state.portfolio[ticker]["current_value"] = st.session_state.portfolio[ticker]["shares"] * current_price
                    
                    # Print debug information to console
                    print(f"DEBUG - Updated portfolio - Ticker: {ticker}")
                    print(f"DEBUG - Shares: {st.session_state.portfolio[ticker]['shares']}")
                    print(f"DEBUG - Cost Basis: {st.session_state.portfolio[ticker]['cost_basis']}")
                    print(f"DEBUG - Current Value: {st.session_state.portfolio[ticker]['current_value']}")
                    
                    # Deduct from cash balance
                    st.session_state.cash_balance -= total_cost
                    
                    # Add to transaction history
                    st.session_state.transaction_history.append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ticker": ticker,
                        "type": "BUY",
                        "shares": shares_to_buy,
                        "price": current_price,
                        "total": total_cost
                    })
                    
                    # Also add to payment history for Payments page tracking
                    st.session_state.payment_history.append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Stock Purchase",
                        "amount": total_cost,
                        "status": "Completed",
                        "details": f"Bought {shares_to_buy} shares of {ticker}"
                    })
                    
                    in_rupees = "INR" in st.session_state.currency
                    currency_symbol = "₹" if in_rupees else "$"
                    st.success(f"Successfully purchased {shares_to_buy} shares of {ticker} for {currency_symbol}{total_cost:.2f}")
                    
                    # Debug information
                    st.write("Portfolio Contents:", st.session_state.portfolio)
                    st.write("Cash Balance:", st.session_state.cash_balance)
                    
                    # Add a button to view portfolio
                    if st.button("Go to Portfolio"):
                        st.session_state.selected_page = "Portfolio"
                        st.rerun()
        
        with col2:
            st.subheader("Sell Shares")
            
            # Check if user owns this stock
            owned_shares = 0
            if ticker in st.session_state.portfolio:
                owned_shares = st.session_state.portfolio[ticker]["shares"]
            
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
            in_rupees = "INR" in st.session_state.currency
            currency_symbol = "₹" if in_rupees else "$"
            st.write(f"Total Value: {currency_symbol}{total_value:.2f}")
            
            if st.button("Sell Shares"):
                if shares_to_sell <= 0:
                    st.error("Please enter a valid number of shares.")
                elif shares_to_sell > owned_shares:
                    st.error("You cannot sell more shares than you own.")
                else:
                    # Update portfolio
                    st.session_state.portfolio[ticker]["shares"] -= shares_to_sell
                    
                    # Calculate average cost per share for proper cost basis reduction
                    avg_cost = st.session_state.portfolio[ticker]["cost_basis"] / (st.session_state.portfolio[ticker]["shares"] + shares_to_sell)
                    cost_reduction = avg_cost * shares_to_sell
                    
                    st.session_state.portfolio[ticker]["cost_basis"] -= cost_reduction
                    st.session_state.portfolio[ticker]["current_value"] = st.session_state.portfolio[ticker]["shares"] * current_price
                    
                    # If no shares left, remove from portfolio
                    if st.session_state.portfolio[ticker]["shares"] == 0:
                        del st.session_state.portfolio[ticker]
                    
                    # Add to cash balance
                    st.session_state.cash_balance += total_value
                    
                    # Add to transaction history
                    st.session_state.transaction_history.append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ticker": ticker,
                        "type": "SELL",
                        "shares": shares_to_sell,
                        "price": current_price,
                        "total": total_value
                    })
                    
                    # Also add to payment history for Payments page tracking
                    st.session_state.payment_history.append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Stock Sale",
                        "amount": total_value,
                        "status": "Completed",
                        "details": f"Sold {shares_to_sell} shares of {ticker}"
                    })
                    
                    in_rupees = "INR" in st.session_state.currency
                    currency_symbol = "₹" if in_rupees else "$"
                    st.success(f"Successfully sold {shares_to_sell} shares of {ticker} for {currency_symbol}{total_value:.2f}")

    elif st.session_state.selected_page == "Portfolio":
        st.title("Your Green Energy Portfolio")
        
        # Debug information
        st.write("Portfolio DEBUG:", st.session_state.portfolio)
        st.write("Session State Keys:", list(st.session_state.keys()))
        
        # Calculate portfolio metrics (for use in all portfolio sections)
        if st.session_state.portfolio:
            metrics = calculate_portfolio_metrics(st.session_state.portfolio)
            total_value = metrics["total_value"]
            total_investments = metrics["total_cost"]
        else:
            total_value = 0
            total_investments = 0
            metrics = {"total_gain_loss": 0, "percent_gain_loss": 0, "sector_allocation": {}}
        
        # Portfolio Overview
        st.header("Portfolio Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
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
                
                # Set currency format based on user preference
                in_rupees = "INR" in st.session_state.currency
                currency_format = "₹%.2f" if in_rupees else "$%.2f"
                
                st.dataframe(
                    holdings_df,
                    column_config={
                        "Current Price": st.column_config.NumberColumn(
                            "Current Price",
                            format=currency_format
                        ),
                        "Market Value": st.column_config.NumberColumn(
                            "Market Value",
                            format=currency_format
                        ),
                        "Cost Basis": st.column_config.NumberColumn(
                            "Cost Basis",
                            format=currency_format
                        ),
                        "Gain/Loss": st.column_config.NumberColumn(
                            "Gain/Loss",
                            format=currency_format
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
        if st.session_state.portfolio and metrics:
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
    
        # Transaction History
        st.header("Transaction History")
        
        if st.session_state.transaction_history:
            transactions_df = pd.DataFrame(st.session_state.transaction_history)
            
            # Set currency format based on user preference
            in_rupees = "INR" in st.session_state.currency
            currency_format = "₹%.2f" if in_rupees else "$%.2f"
            
            st.dataframe(
                transactions_df,
                column_config={
                    "date": st.column_config.DatetimeColumn(
                        "Date",
                        format="YYYY-MM-DD HH:mm"
                    ),
                    "price": st.column_config.NumberColumn(
                        "Price",
                        format=currency_format
                    ),
                    "total": st.column_config.NumberColumn(
                        "Total",
                        format=currency_format
                    ),
                },
                use_container_width=True
            )
        else:
            st.info("No transaction history yet.")
        
        # Portfolio reset option
        st.header("Portfolio Management")
        
        if st.button("Reset Portfolio"):
            st.session_state.portfolio = {}
            st.session_state.cash_balance = DEFAULT_PORTFOLIO_BALANCE
            st.session_state.transaction_history = []
            st.success("Portfolio has been reset to initial state.")
            st.rerun()

# Market Analysis page
if st.session_state.selected_page == "Market Analysis":
    st.title("Green Energy Market Analysis")
    
    # Get period from session state
    period = st.session_state.selected_period
    
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
        comparison_data = get_multiple_stocks_data(selected_tickers, period=period)
        
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
                yaxis_title="Price (₹)",
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
            stock_data = get_stock_data(ticker, period=period)
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
                        format="₹%.2f"
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
                        format="₹%.2f"
                    )
                },
                use_container_width=True
            )
            
            # Plot performance of all stocks in the sector
            sector_tickers = sector_stocks['Ticker'].tolist()
            sector_data = get_multiple_stocks_data(sector_tickers, period=period)
            
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
    else:
        st.info("Loading ESG analysis data...")

# Payments page
elif st.session_state.selected_page == "Payments":
    st.title("Payment Gateway & Transaction History")
    
    # Display current portfolio and total value for reference
    st.subheader("Your Current Portfolio")
    
    # Calculate portfolio value
    total_portfolio_value = 0
    for ticker, holding in st.session_state.portfolio.items():
        total_portfolio_value += holding['current_value']
    
    total_assets = total_portfolio_value + st.session_state.cash_balance
    in_rupees = "INR" in st.session_state.currency
    currency_symbol = "₹" if in_rupees else "$"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Portfolio Value",
            format_large_number(total_portfolio_value, in_rupees=in_rupees),
            None
        )
    
    with col2:
        st.metric(
            "Cash Balance",
            format_large_number(st.session_state.cash_balance, in_rupees=in_rupees),
            None
        )
    
    with col3:
        st.metric(
            "Total Assets",
            format_large_number(total_assets, in_rupees=in_rupees),
            None
        )
    
    # Add funds section
    st.header("Add Funds to Your Account")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Payment methods
        st.subheader("Payment Methods")
        
        # Add payment method form
        payment_type = st.selectbox(
            "Payment Method",
            ["Credit Card", "Debit Card", "UPI", "Net Banking"]
        )
        
        if payment_type in ["Credit Card", "Debit Card"]:
            st.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Expiry Date", placeholder="MM/YY")
            with col2:
                st.text_input("CVV", placeholder="XXX", type="password")
            st.text_input("Cardholder Name", placeholder="Name on card")
        
        elif payment_type == "UPI":
            st.text_input("UPI ID", placeholder="yourname@upi")
        
        elif payment_type == "Net Banking":
            st.selectbox(
                "Select Bank",
                ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Mahindra Bank"]
            )
            st.text_input("User ID", placeholder="Bank User ID")
    
    with col2:
        st.subheader("Amount to Add")
        amount = st.number_input(
            "Enter Amount",
            min_value=1000.0,
            max_value=1000000.0,
            value=10000.0,
            step=1000.0
        )
        
        st.markdown(f"**Total: {currency_symbol}{amount:.2f}**")
        
        if st.button("Add Funds"):
            # Add to cash balance
            st.session_state.cash_balance += amount
            
            # Add to payment history
            st.session_state.payment_history.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": payment_type,
                "amount": amount,
                "status": "Completed"
            })
            
            st.success(f"Successfully added {currency_symbol}{amount:.2f} to your account!")
            st.balloons()
            st.rerun()
    
    # Button to buy more stocks
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Buy New Stocks"):
            st.session_state.selected_page = "Companies"
            st.rerun()
    
    # Stock purchase history
    st.header("Stock Purchase History")
    
    if st.session_state.transaction_history:
        transactions_df = pd.DataFrame(st.session_state.transaction_history)
        
        # Set currency format based on user preference
        currency_format = "₹%.2f" if in_rupees else "$%.2f"
        
        st.dataframe(
            transactions_df,
            column_config={
                "date": st.column_config.DatetimeColumn(
                    "Date",
                    format="YYYY-MM-DD HH:mm"
                ),
                "price": st.column_config.NumberColumn(
                    "Price",
                    format=currency_format
                ),
                "total": st.column_config.NumberColumn(
                    "Total",
                    format=currency_format
                ),
            },
            use_container_width=True
        )
    else:
        st.info("No stock transaction history yet.")
    
    # Payment history
    st.header("Payment History")
    
    if st.session_state.payment_history:
        payments_df = pd.DataFrame(st.session_state.payment_history)
        
        # Set currency format based on user preference
        currency_format = "₹%.2f" if in_rupees else "$%.2f"
        
        st.dataframe(
            payments_df,
            column_config={
                "date": st.column_config.DatetimeColumn(
                    "Date",
                    format="YYYY-MM-DD HH:mm"
                ),
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format=currency_format
                ),
                "status": st.column_config.TextColumn("Status"),
                "type": st.column_config.TextColumn("Payment Method")
            },
            use_container_width=True
        )
    else:
        st.info("No payment history yet.")

# Account page 
elif st.session_state.selected_page == "Account":
    st.title("Account Settings")
    
    # User profile
    st.header("User Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div style="background-color: #1E2127; padding: 20px; border-radius: 10px; text-align: center;">
            <div style="font-size: 40px; color: #16B174; margin-bottom: 10px;">👤</div>
            <div style="font-weight: bold; font-size: 18px; margin-bottom: 5px;">{}</div>
            <div style="color: #9FA2A7;">Active</div>
        </div>
        """.format(st.session_state.username), unsafe_allow_html=True)
    
    with col2:
        st.text_input("Full Name", value="John Doe")
        st.text_input("Email Address", value="john.doe@example.com")
        st.text_input("Phone Number", value="+91 9876543210")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Country", ["India", "United States", "United Kingdom", "Singapore", "Australia"])
        with col2:
            st.text_input("PAN Number", value="ABCDE1234F", help="Required for tax purposes")
        
        if st.button("Update Profile"):
            st.success("Profile updated successfully!")
    
    # Settings
    st.header("Settings")
    
    st.subheader("Notification Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Price Alerts", value=True)
        st.checkbox("Portfolio Updates", value=True)
    
    with col2:
        st.checkbox("Market News", value=True)
        st.checkbox("Trading Confirmations", value=True)
    
    st.subheader("Security Settings")
    
    st.toggle("Two-Factor Authentication", value=False)
    
    # Signout option
    st.header("Account Actions")
    
    if st.button("Sign Out"):
        st.session_state.user_logged_in = False
        st.session_state.username = ""
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.caption("Green Energy Stock Exchange Platform | Data provided by Yahoo Finance | Developed with Streamlit")
