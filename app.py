# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from data import load_all
from models import forecast_series
import datetime
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Crypto Market Dashboard", layout="wide")

# Sidebar controls
st.sidebar.title("Controls")
coins = st.sidebar.multiselect(
    "Select coins (CoinGecko IDs)",
    ['bitcoin', 'ethereum', 'binancecoin', 'solana'],
    default=['bitcoin', 'ethereum']
)
date_range = st.sidebar.date_input(
    "Date range",
    [datetime.date.today() - datetime.timedelta(days=365), datetime.date.today()]
)
horizon = st.sidebar.selectbox("Forecast horizon (days)", [7, 14, 30, 60], index=2)
alert_thresh = st.sidebar.slider("Alert: drop > % in 24h", 0, 100, 10)
send_alert = st.sidebar.checkbox("Enable alert emails")
fred_key = st.sidebar.text_input("FRED API Key", type="password")
keywords = st.sidebar.text_input(
    "Google Trends keywords (comma-separated)",
    "buy bitcoin,ethereum price"
).split(',')

# Load data
try:
    df = load_all(coins, fred_key, keywords)
    df = df.loc[date_range[0]:date_range[1]]
    
    # Ensure numeric columns are properly typed
    for col in df.columns:
        if col in coins or col in ['btc_dominance', 'value', 'fear_greed']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Summary cards
    latest = df.iloc[-1]
    cols = st.columns(len(latest))
    for i, (k, v) in enumerate(latest.items()):
        # Only calculate delta for numeric values
        if pd.api.types.is_numeric_dtype(df[k]) and not pd.isna(v):
            try:
                previous_value = df.shift(1).iloc[-1][k]
                if not pd.isna(previous_value):
                    delta = v - previous_value
                    cols[i].metric(label=k, value=f"{v:.2f}", delta=f"{delta:.2f}")
                else:
                    cols[i].metric(label=k, value=f"{v:.2f}")
            except (TypeError, ValueError, IndexError):
                cols[i].metric(label=k, value=f"{v:.2f}")
        else:
            # For non-numeric values, just display the value
            cols[i].metric(label=k, value=str(v))

    # Time series plots
    st.header("Time Series Charts")
    
    # Only plot coins that exist and have numeric data
    available_coins = [coin for coin in coins if coin in df.columns and pd.api.types.is_numeric_dtype(df[coin])]
    if available_coins:
        st.plotly_chart(px.line(df[available_coins], title="Market Cap"), use_container_width=True)
    
    if 'btc_dominance' in df.columns:
        st.plotly_chart(px.line(df['btc_dominance'], title="Bitcoin Dominance (%)"), use_container_width=True)
    
    if 'value' in df.columns:
        st.plotly_chart(px.line(df['value'], title="M2 Money Supply"), use_container_width=True)
    
    if 'fear_greed' in df.columns:
        st.plotly_chart(px.line(df['fear_greed'], title="Crypto Fear & Greed Index"), use_container_width=True)
    
    # Check if keyword columns exist
    available_keywords = [kw for kw in keywords if kw in df.columns]
    if available_keywords:
        st.plotly_chart(px.line(df[available_keywords], title="Google Trends"), use_container_width=True)

    # Correlation heatmap
    st.header("Correlation Matrix")
    # Only include numeric columns for correlation
    numeric_df = df.select_dtypes(include=[float, int])
    if not numeric_df.empty:
        st.plotly_chart(px.imshow(numeric_df.corr(), text_auto=True), use_container_width=True)
    else:
        st.warning("No numeric data available for correlation matrix")

    # Forecasting
    st.header("Forecasting")
    for coin in available_coins:
        try:
            fc, mae, rmse = forecast_series(df, coin, periods=horizon)
            fig = px.line(fc, x='ds', y=['yhat'], title=f"{coin} Forecast (MAE={mae:.2f}, RMSE={rmse:.2f})")
            fig.add_scatter(x=fc['ds'], y=fc['yhat_lower'], mode='lines', showlegend=False)
            fig.add_scatter(x=fc['ds'], y=fc['yhat_upper'], mode='lines', fill='tonexty', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error forecasting {coin}: {str(e)}")

    # Alerts
    if send_alert:
        # Only check numeric coin columns for price drops
        numeric_coins = [coin for coin in available_coins if pd.api.types.is_numeric_dtype(df[coin])]
        if numeric_coins:
            try:
                drop = (df[numeric_coins].pct_change().iloc[-1] * 100).min()
                if drop < -alert_thresh:
                    msg = EmailMessage()
                    msg.set_content(f"Alert: market cap dropped {drop:.2f}% in last 24h.")
                    msg['Subject'] = "Crypto Dashboard Alert"
                    msg['From'] = st.sidebar.text_input("From email")
                    msg['To'] = st.sidebar.text_input("To email")
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    pwd = st.sidebar.text_input("Email password", type="password")
                    server.login(msg['From'], pwd)
                    server.send_message(msg)
                    server.quit()
                    st.warning(f"Alert sent: drop={drop:.2f}%")
            except Exception as e:
                st.error(f"Error with alert system: {str(e)}")

    # Download CSV
    st.download_button("Download data as CSV", df.to_csv().encode('utf-8'), "crypto_data.csv")

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please check your API keys and internet connection.")