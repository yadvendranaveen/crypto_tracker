# Crypto Market Dashboard

A real-time cryptocurrency market dashboard built with Streamlit that provides comprehensive market analysis, forecasting, and alerting capabilities.

## Features

- **Real-time Market Data**: Track multiple cryptocurrencies using CoinGecko API
- **Bitcoin Dominance**: Monitor BTC market dominance
- **Economic Data**: M2 money supply integration (requires FRED API key)
- **Sentiment Analysis**: Crypto Fear & Greed Index
- **Google Trends**: Track crypto-related search trends
- **Forecasting**: Prophet-based price predictions
- **Correlation Analysis**: Visualize relationships between different metrics
- **Email Alerts**: Get notified of significant price drops
- **Data Export**: Download historical data as CSV

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment: `source .venv/bin/activate` (Mac/Linux) or `.venv\Scriptsctivate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the app: `streamlit run app.py`

## API Keys

- **FRED API Key**: Optional, for M2 money supply data
- **Email Configuration**: Optional, for alert notifications

## Usage

The dashboard will be available at `http://localhost:8501`. Use the sidebar to:
- Select cryptocurrencies to track
- Set date ranges
- Configure forecast horizons
- Set up alerts and notifications

## Technologies

- Streamlit for web interface
- Plotly for interactive charts
- Prophet for time series forecasting
- Pandas for data manipulation
- CoinGecko API for crypto data
- FRED API for economic data
- Google Trends via pytrends
