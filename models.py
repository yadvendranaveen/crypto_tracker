# models.py

import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def forecast_series(df, column, periods=30):
    # Ensure we have a clean dataframe with the right structure
    ts_data = df[[column]].copy()
    ts_data = ts_data.dropna()  # Remove any NaN values
    
    # Reset index to get date as a column
    ts = ts_data.reset_index()
    
    # Rename columns to what Prophet expects
    if 'date' in ts.columns:
        ts = ts.rename(columns={'date': 'ds', column: 'y'})
    else:
        # If index doesn't have name 'date', use the index anyway
        ts.index.name = 'ds'
        ts = ts.reset_index()
        ts = ts.rename(columns={column: 'y'})
    
    # Ensure ds column is datetime
    ts['ds'] = pd.to_datetime(ts['ds'])
    
    # Ensure y column is numeric
    ts['y'] = pd.to_numeric(ts['y'], errors='coerce')
    ts = ts.dropna()  # Remove any rows where conversion failed
    
    if len(ts) < 2:
        raise ValueError(f"Insufficient data for forecasting {column}")
    
    model = Prophet()
    model.fit(ts)
    future = model.make_future_dataframe(periods=periods)
    fc = model.predict(future)

    # Metrics on historical fit
    hist = fc[fc['ds'] <= ts['ds'].max()]
    y_true = ts['y']
    y_pred = hist['yhat']
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    return fc[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], mae, rmse