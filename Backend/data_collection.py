from polygon import RESTClient
import json
from typing import cast
from urllib3 import HTTPResponse
import time
import pandas as pd
from datetime import datetime
from_date = "2023-01-01"
to_date = datetime.now().strftime("%Y-%m-%d")


def get_polygon_data(symbol):
    print(f"Pulling Polygon Data for {symbol}")
    client = RESTClient(api_key="W68dixyjP1O1Z_Ky1bkKSfOcxkInBNIz")
    close = []
    date = []
    open = []
    high = []
    low = []

    bars = cast(HTTPResponse, client.get_aggs(ticker=symbol, multiplier=1, timespan="day", from_=from_date, to= to_date, raw=True),)
    data = json.loads(bars.data)
    df = pd.DataFrame()

    for item in data:
        if item == 'results':
            aggdata = data[item]
    for bar in aggdata:
        for category in bar:
            if category == 'c':
                close.append(bar[category])
            if category == 't':
                y = (bar[category]/1000)
                x = datetime.fromtimestamp(y)
                z = x.strftime('%Y-%m-%d')
                date.append(z)
            if category == 'o':
                open.append(bar[category])
            if category == 'h':
                high.append(bar[category])
            if category == 'l':
                low.append(bar[category])


    df['close'] = close
    df.index = date
    df['open'] = open
    df['high'] = high
    df['low'] = low
 
    return df

def calculate_stoch_rsi_and_sma(stocks, period1, period2,):
    df = pd.DataFrame()
    
    for stock in stocks:
        stock_data = get_polygon_data(stock)
        df_osc = pd.DataFrame()
        df_osc['lowestlow'] = stock_data['low'].rolling(window=14).min()
        df_osc['highesthigh'] = stock_data['high'].rolling(window=14).max()
        df_osc['%K'] = 100 * (stock_data['close'] - df_osc['lowestlow']) / (df_osc['highesthigh'] - df_osc['lowestlow'])
        df_osc['%D'] = df_osc['%K'].rolling(window=3, min_periods=3).mean()
        
        
        close_data = stock_data['close']
        sma_period1 = close_data.rolling(window=period1).mean()
        sma_period2 = close_data.rolling(window=period2).mean()
        df[f'{stock} Stochastic Oscillator K'] = df_osc['%K']
        df[f'{stock} Stochastic Oscillator D'] = df_osc['%D']
        df[f'{stock} {period1} day SMA'] = sma_period1
        df[f'{stock} {period2} day SMA'] = sma_period2
        df.index = stock_data.index
        df[f'{stock} high'] = stock_data['high']
        df[f'{stock} low'] = stock_data['low']
        df[f'{stock} close'] = close_data
        df[f'{stock} open'] = stock_data['open']
        
        time.sleep(12)
    print("Polygon Data Collected")
    return df
  

