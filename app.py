import time
from alpaca.trading.client import TradingClient
import alpaca_trade_api as tradeapi
from datetime import datetime
import pandas as pd
import data_collection
import math
import trading_decisions
import requests
import json
import sqlite3


POLYGON_API_KEY = 'W68dixyjP1O1Z_Ky1bkKSfOcxkInBNIz'
polygon_url = 'https://api.polygon.io/v2/aggs/ticker/{symbol}/prev'
alpaca_api_key = 'PKERWL1FLVEWYGLURCK1'
alpaca_secret_key = 'ywdogDK0seRmSvPptlTBzEeaL5czuPKyQdomBTn8'
base_url='https://paper-api.alpaca.markets'
#stocks = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'META', 'TSLA', 'GOOGL', 'AVGO', 'PEP', 'COST']
stocks = ['AAPL']
stock_data = data_collection.calculate_stoch_rsi_and_sma(stocks, 20, 50)
signals, trend_df = trading_decisions.check_stochastic_intersections_and_SMA(stock_data, stocks)
fib_df = trading_decisions.calculate_fib_numbers(stocks, stock_data)
output_df = trading_decisions.check_signals(stock_data, stocks, signals, trend_df, fib_df)

def place_market_order(ticker, qty, side, type, time_in_force, take_profit=None, stop_loss=None):
    api = tradeapi.REST(alpaca_api_key, alpaca_secret_key, base_url=base_url)
    api.submit_order(symbol=ticker,qty=qty,side=side,type=type,time_in_force=time_in_force, take_profit=take_profit, stop_loss=stop_loss)
    order = f"Market order placed: Side: {side} Qty: {qty} Ticker: {ticker} Order type: {type} Time in force: {time_in_force} Take profit: {take_profit} Stop loss: {stop_loss}"
    return order

def check_buying_power(api_key, secret_key):
    trading_client = TradingClient(api_key, secret_key)
    account = trading_client.get_account()
    return account.buying_power

def check_positions_for_a_ticker(api_key, secret_key, ticker):
    trading_client = TradingClient(api_key, secret_key)
    positions = trading_client.get_all_positions()
    positions_dict = {}
    for position in positions:
        ticker = position.symbol
        qty = position.qty
        side = position.side.name
    positions_dict[ticker] = {'qty': qty, 'side': side}
    position_data = positions_dict.get(ticker)
    if position_data is not None:
        return position_data
    else:
        return None
def run_algorithm():
    if datetime.today().weekday in [5,6]:
        data = "The Market is not open on weekdays"
        return
    for stock in stocks:
        buying_power = check_buying_power(alpaca_api_key, alpaca_secret_key)
        if output_df.loc[0, f'{stock}'] == 'Sell':
            position_data = check_positions_for_a_ticker(alpaca_api_key, alpaca_secret_key, stock)
            if position_data.get('qty') != 0:
                if position_data.get('side') == 'LONG':
                    data = place_market_order(stock, position_data.get('qty'), 'sell', 'market', 'gtc')
            else:
                if buying_power > (stock_data[f'{stock} close'].iloc[-1] * 10):
                    shares = (stock_data[f'{stock} close'].iloc[-1] / 5000)
                    shares2 = math.floor(shares)
                    place_market_order(ticker=stock, qty=shares2, side='sell', type='market', time_in_force='day', take_profit=(stock_data[f'{stock} close'].iloc[-1] * 1.1), stop_loss=(stock_data[f'{stock} close'].iloc[-1] * 0.9))
        elif output_df.loc[0, f'{stock}'] == 'Buy':
            position_data = check_positions_for_a_ticker(alpaca_api_key, alpaca_secret_key, stock)
            if position_data.get('qty') != 0:
                if position_data.get('side') == 'SHORT':
                    place_market_order(stock, position_data.get('qty'), 'buy', 'market', 'gtc')
            else:
                if buying_power > (stock_data.loc[0, f'{stock} close'] * 10):
                    shares = (stock_data.loc[0, f'{stock} close']/ 5000)
                    shares2 = math.floor(shares)
                    place_market_order(ticker=stock, qty=shares2, side='buy', type='market', time_in_force='day', take_profit=(stock_data.loc[0, f'{stock} close'] * 1.1), stop_loss=(stock_data.loc[0, f'{stock} close'] * 0.9))
        elif output_df.loc[0, f'{stock}'] == 'Hold':
            data = f'Hold Signal Received for {stock}'
    return data

db_path = '/Users/houstonprewett/Desktop/Python/Alpaca/data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the algorithm_logs table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS alpaca_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        time DATETIME
    )
''')
conn.commit()


def generate_json_from_database(database_path, output_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM alpaca_logs")
    
    rows = cursor.fetchall()

    data = []
    for row in rows:
        item = {
            'Action': row[1],
            'Time': row[2],
        }
        data.append(item)
    
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file)
    conn.close()

def lambda_handler (event, context):
    data = run_algorithm()
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO alpaca_logs (action, time) VALUES (?, ?)', (data, formatted_time))
    conn.commit()
    print('Log message stored in the database')
    generate_json_from_database(db_path, '/Backend/output.json')
    print('json file updated')
    
lambda_handler(None, None)


