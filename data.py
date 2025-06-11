# data.py

import pandas as pd
import requests
from pytrends.request import TrendReq
import datetime

COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_coin_marketcap(coins, vs_currency='usd', days=365):
    end = datetime.datetime.today()
    start = end - datetime.timedelta(days=days)
    frames = []
    for coin in coins:
        url = f"{COINGECKO_API}/coins/{coin}/market_chart/range"
        params = {
            'vs_currency': vs_currency,
            'from': int(start.timestamp()),
            'to': int(end.timestamp())
        }
        data = requests.get(url, params=params).json()
        if 'market_caps' not in data:
            raise ValueError(f"No market_caps data for coin: {coin}")
        df = pd.DataFrame(data['market_caps'], columns=['timestamp', coin])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
        df = df[['date', coin]]
        frames.append(df.set_index('date'))
    return pd.concat(frames, axis=1)

def get_bitcoin_dominance(coins, days=365):
    df_mc = get_coin_marketcap(coins, days=days)
    dom = df_mc['bitcoin'] / df_mc.sum(axis=1) * 100
    return dom.to_frame('btc_dominance')

# def get_m2_money_supply(api_key, series_id='M2SL'):
#     url = "https://api.stlouisfed.org/fred/series/observations"
#     params = {'series_id': series_id, 'api_key': api_key, 'file_type': 'json'}
#     data = requests.get(url, params=params).json()
#     df = pd.DataFrame(data['observations'])[['date', 'value']]
#     df['value'] = pd.to_numeric(df['value'], errors='coerce')
#     df['date'] = pd.to_datetime(df['date']).dt.date
#     return df.set_index('date')
def get_m2_money_supply(api_key, series_id='M2SL'):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {'series_id': series_id, 'api_key': api_key, 'file_type': 'json'}
    data = requests.get(url, params=params).json()

    # If the key's bad you'll end up here:
    if 'observations' not in data:
        # return an empty frame you can merge on later
        return pd.DataFrame(columns=['value'])

    df = pd.DataFrame(data['observations'])[['date', 'value']]
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df.set_index('date')

def get_fear_greed_index():
    url = "https://api.alternative.me/fng/"
    data = requests.get(url).json()
    df = pd.DataFrame(data['data'])[['timestamp', 'value']]
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.set_index('date').rename(columns={'value': 'fear_greed'})

def get_google_trends(keywords, timeframe='today 12-m'):
    pytrends = TrendReq()
    pytrends.build_payload(keywords, timeframe=timeframe)
    df = pytrends.interest_over_time()
    if 'isPartial' in df:
        df = df.drop(columns=['isPartial'])
    df.index = df.index.date
    return df

def load_all(coins, fred_key, keywords, days=365):
    df_mc = get_coin_marketcap(coins, days=days)
    df_dom = get_bitcoin_dominance(coins, days=days)
    df_m2 = get_m2_money_supply(fred_key)
    df_fg = get_fear_greed_index()
    df_tr = get_google_trends(keywords)
    df = pd.concat([df_mc, df_dom, df_m2, df_fg, df_tr], axis=1)
    df = df.sort_index()
    df = df.interpolate().ffill()
    return df