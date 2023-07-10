
from alpaca.trading.client import TradingClient
import alpaca_trade_api as tradeapi
from datetime import datetime
import data_collection
import pandas
import math
import trading_decisions
import config
import account
import json
import sqlite3
from github import Github
from github import Auth


repo_owner = config.repo_owner
repo_name = config.repo_name
github_token = config.github_token
local_database_path = config.local_database_path
alpaca_api_key = config.alpaca_api_key
alpaca_secret_key = config.alpaca_secret_key
base_url= config.base_url


stocks = ['MSFT', 'AAPL', 'NVDA', 'AMZN', 'META', 'TSLA', 'GOOGL', 'AVGO', 'PEP', 'COST']

stock_data = data_collection.calculate_stoch_rsi_and_sma(stocks, 20, 50)
signals, trend_df = trading_decisions.check_stochastic_intersections_and_SMA(stock_data, stocks)
fib_df = trading_decisions.calculate_fib_numbers(stocks, stock_data)
output_df = trading_decisions.check_signals(stock_data, stocks, signals, trend_df, fib_df)

def run_algorithm():
    data = []
    if datetime.today().weekday() in [5,6]:
        data.append("The Market is not open on weekends")
        return data
    for stock in stocks:
        buying_power = account.check_buying_power(alpaca_api_key, alpaca_secret_key)
        if output_df.loc[0, f'{stock}'] == 'Sell':
            print(f'Sell Signal received for {stock}')
            position_data = account.check_positions_for_a_ticker(alpaca_api_key, alpaca_secret_key, stock)
            if position_data is not None:
                if position_data.get('side') == 'LONG':
                    print(f'You are long on {stock}, closing your position')
                    order = account.place_market_order(alpaca_api_key, alpaca_secret_key, base_url, stock, position_data.get('qty'), 'sell', 'market', 'gtc')
                    data.append(order)
            else:
                if buying_power > (5000/stock_data[f'{stock} close'].iloc[-1]):
                    print(f'You do not have an open position, placing a short order on {stock}')
                    shares = (5000/stock_data[f'{stock} close'].iloc[-1])
                    shares2 = math.floor(shares)
                    qty_to_sell = shares2
                    order = account.place_market_order(alpaca_api_key, alpaca_secret_key, base_url, stock, qty_to_sell, 'sell', 'market', 'day', take_profit=float(stock_data[f'{stock} close'].iloc[-1] * 1.1), stop_loss=float(stock_data[f'{stock} close'].iloc[-1] * 0.9))
                    data.append(order)
        elif output_df.loc[0, f'{stock}'] == 'Buy':
            print(f'Buy signal received for {stock}')
            position_data = account.check_positions_for_a_ticker(alpaca_api_key, alpaca_secret_key, stock)
            if position_data is not None:
                if position_data.get('side') == 'SHORT':
                    print(f'You are short on {stock}, closing your position')
                    order = account.place_market_order(alpaca_api_key, alpaca_secret_key, base_url, stock, position_data.get('qty'), 'buy', 'market', 'gtc')
                    data.append(order)
            else:
                if buying_power > (stock_data.loc[0, f'{stock} close'] * 10):
                    print(f'You do not have an open position, placing a long order for {stock}')
                    shares = (5000/stock_data.loc[0, f'{stock} close'])
                    shares2 = math.floor(shares)
                    order = account.place_market_order(alpaca_api_key, alpaca_secret_key, base_url, stock, shares2, 'buy', 'market', 'day', take_profit=float(stock_data.loc[0, f'{stock} close'] * 1.1), stop_loss=float(stock_data.loc[0, f'{stock} close'] * 0.9))
                    data.append(order)
        elif output_df.loc[0, f'{stock}'] == 'Hold':
            print(f'Hold signal received for {stock}')
            data.append(f'Hold Signal Received for {stock}')
    return data


def database_edit(data, formatted_time, positions_output, portfolio_history):
    conn = sqlite3.connect(local_database_path)
    cursor = conn.cursor()


    cursor.execute('''
            CREATE TABLE IF NOT EXISTS alpaca_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                time DATETIME
            )
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS alpaca_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                pl FLOAT,
                qty FLOAT
            )
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_history (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   equity FLOAT,
                   pl FLOAT,
                   time DATETIME
            )
        ''')
    cursor.execute('DELETE FROM alpaca_positions')
    cursor.execute('DELETE FROM portfolio_history')
    conn.commit()
    for signal in data:
        cursor.execute('INSERT INTO alpaca_signals (action, time) VALUES (?, ?)', (signal, formatted_time))
        conn.commit()
    for position in positions_output:
        symbol = position['symbol']
        pl = position['Unrealized Profit/Loss']
        qty = position['Quantity']
        cursor.execute('INSERT INTO alpaca_positions (symbol, pl, qty) VALUES (?, ?, ?)', (symbol, pl, qty))
        conn.commit()
    for history in portfolio_history:
        equity = history['equity']
        profit_loss = history['profit_loss']
        date = history['date']
        cursor.execute('INSERT INTO portfolio_history (equity, pl, time) VALUES (?, ?, ?)', (equity, profit_loss, date))
        conn.commit()

def generate_signal_json_from_database(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM alpaca_signals")
    
    rows = cursor.fetchall()

    data = []
    for row in rows:
        item = {
            'Action': row[1],
            'Time': row[2],
        }
        data.append(item)
    
    new_content = json.dumps(data)
     
    return new_content
def generate_positions_json_from_database(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alpaca_positions")
    rows = cursor.fetchall()
    data = []
    for row in rows:
        item = {
            'Symbol': row[1],
            'Profit/Loss on Position': row[2],
            'Quantity': row[3]
        }
        data.append(item)
    new_content = json.dumps(data)
    return new_content
def generate_history_json_from_database(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolio_history")
    rows = cursor.fetchall()
    data = []
    for row in rows:
        item = {
            'equity': row[1],
            'profit_loss': row[2],
            'date': row[3]
        }
        data.append(item)
    new_content = json.dumps(data)
    return new_content
def update_github_file(repo_owner, repo_name, file_path, access_token, new_content):
    auth = Auth.Token(access_token)
    g = Github(auth=auth)
    repo = g.get_repo(f'{repo_owner}/{repo_name}')
    file = repo.get_contents(file_path)
    repo.update_file(file_path, 'Changed json', new_content, file.sha)

    print("File updated successfully.")

def run_and_update_website ():
    data = run_algorithm()
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    positions_ouput = account.check_portfolio_positions(alpaca_api_key, alpaca_secret_key)
    portfolio_history = account.get_portfolio_history(alpaca_api_key, alpaca_secret_key)
    database_edit(data, formatted_time, positions_ouput, portfolio_history)
    print('Log message stored in the database')
    new_content = generate_signal_json_from_database(local_database_path)
    new_content2 = generate_positions_json_from_database(local_database_path)
    new_content3 = generate_history_json_from_database(local_database_path)
    update_github_file(repo_owner, repo_name, 'Backend/output.json', github_token, new_content)
    update_github_file(repo_owner, repo_name, 'Backend/positions.json', github_token, new_content2)
    update_github_file(repo_owner, repo_name, 'Backend/portfolio_history.json', github_token, new_content3)

run_and_update_website()



