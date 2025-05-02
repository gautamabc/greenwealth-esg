"""
Configuration file for the Green Energy Stock Exchange Platform.
Contains constants and settings used throughout the application.
"""

# List of green energy companies to track
# Format: (Ticker Symbol, Company Name, Sector)
GREEN_ENERGY_STOCKS = [
    ("ENPH", "Enphase Energy", "Solar"),
    ("SEDG", "SolarEdge Technologies", "Solar"),
    ("FSLR", "First Solar", "Solar"),
    ("RUN", "Sunrun Inc.", "Solar"),
    ("CSIQ", "Canadian Solar", "Solar"),
    ("NEE", "NextEra Energy", "Renewable Energy"),
    ("BEP", "Brookfield Renewable Partners", "Renewable Energy"),
    ("VWDRY", "Vestas Wind Systems", "Wind"),
    ("PLUG", "Plug Power", "Hydrogen & Fuel Cell"),
    ("BLDP", "Ballard Power Systems", "Hydrogen & Fuel Cell"),
    ("BE", "Bloom Energy", "Hydrogen & Fuel Cell"),
    ("NIO", "NIO Inc.", "Electric Vehicles"),
    ("TSLA", "Tesla, Inc.", "Electric Vehicles"),
    ("LCID", "Lucid Group", "Electric Vehicles"),
    ("RIVN", "Rivian Automotive", "Electric Vehicles"),
    ("ALB", "Albemarle Corporation", "Battery Materials"),
]

# Default time periods for stock charts
TIME_PERIODS = {
    "1D": "1d",
    "1W": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "YTD": "ytd",
    "1Y": "1y",
    "5Y": "5y",
    "MAX": "max",
}

# ESG Score ranges and interpretations
ESG_SCORE_RANGES = {
    "Excellent": (80, 100),
    "Good": (60, 79),
    "Average": (40, 59),
    "Below Average": (20, 39),
    "Poor": (0, 19),
}

# Portfolio initial investment amount (in INR)
DEFAULT_PORTFOLIO_BALANCE = 8000000.00  # 80 Lakhs INR (equivalent to ~$100,000)

# USD to INR conversion rate
USD_TO_INR_RATE = 83.5  # Example conversion rate, updated regularly in production

# Market hours (IST)
MARKET_HOURS = {
    "open": "9:15",
    "close": "15:30"
}

# News update frequency (in minutes)
NEWS_UPDATE_FREQUENCY = 15

# Alert thresholds
ALERT_THRESHOLDS = {
    "price_change_percent": 5.0,  # Alert when price changes by 5%
    "volume_spike_percent": 200.0  # Alert when volume spikes 200% above average
}
