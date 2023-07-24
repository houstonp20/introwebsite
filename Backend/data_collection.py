import yfinance as yf
import pandas as pd
from datetime import datetime
import time
from_date = "2023-01-01"
to_date = datetime.now().strftime("%Y-%m-%d")


def get_stock_data (stock):
    print(f'Collecting Data for {stock}. Like a boss.')
    df = pd.DataFrame()
    ticker = yf.Ticker(stock)
    hist = ticker.history(start=from_date, end=to_date, interval= '1d')
    df = hist.copy()
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    df = df.rename(columns={'High':'high', 'Low':'low', 'Open':'open', 'Close':'close'})
    return df

def calculate_stoch_rsi_and_sma(stocks, period1, period2,):
    df = pd.DataFrame()
    
    for stock in stocks:
        stock_data = get_stock_data(stock)
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

    print("Stock Data Collected")
    return df
  

