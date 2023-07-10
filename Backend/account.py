from alpaca.trading.client import TradingClient
import alpaca_trade_api as tradeapi
from datetime import datetime


def place_market_order(api_key, secret_key, base_url, ticker, qty, side, type, time_in_force, take_profit=None, stop_loss=None):
    api = tradeapi.REST(api_key, secret_key, base_url=base_url)
    api.submit_order(symbol=ticker,qty=qty,side=side,type=type,time_in_force=time_in_force, take_profit={'limit price': take_profit}, stop_loss={'stop price': stop_loss})
    order = f"Market order placed: Side: {side} Qty: {qty} Ticker: {ticker} Order type: {type} Time in force: {time_in_force} Take profit: {take_profit} Stop loss: {stop_loss}"
    print(f'Order placed for {ticker}')
    return order

def check_buying_power(api_key, secret_key):
    trading_client = TradingClient(api_key, secret_key)
    account = trading_client.get_account()
    return float(account.buying_power)

def check_portfolio_positions(api_key, secret_key):
    trading_client = TradingClient(api_key, secret_key)
    account = trading_client.get_all_positions()
    output = []
    for position in account:
        positions = {}
        symbol = position.symbol
        pl_str = position.unrealized_pl
        pl = float(pl_str)
        qty_str = position.qty
        qty = float(qty_str)
        positions = {'symbol': symbol, 'Unrealized Profit/Loss': pl, 'Quantity': qty}
        output.append(positions)
    return output

def check_positions_for_a_ticker(api_key, secret_key, ticker):
    trading_client = TradingClient(api_key, secret_key)
    positions = trading_client.get_all_positions()
    positions_dict = {}
    for position in positions:
        symbol = position.symbol
        qty = position.qty
        side = position.side.name
    positions_dict[symbol] = {'qty': qty, 'side': side}
    position_data = positions_dict.get(ticker)
    if position_data is not None:
        return position_data
    else:
        return None
def get_portfolio_history (api_key, secret_key):
    api = tradeapi.REST(api_key, secret_key, base_url='https://paper-api.alpaca.markets')
    ph = api.get_portfolio_history()
    equity = ph.equity
    profit_loss = ph.profit_loss
    time = ph.timestamp
    date_time_list = []
    for timestamp in time:
        date_time = datetime.fromtimestamp(timestamp)
        formatted_time = date_time.strftime('%Y-%m-%d')
        date_time_list.append(formatted_time)
    portfolio_history = []
    for equity_object, profit_loss_object, date in zip(equity, profit_loss, date_time_list):
        portfolio_dictionary = {
            'equity': equity_object,
            'profit_loss': profit_loss_object,
            'date': date
        }
        portfolio_history.append(portfolio_dictionary)
    return portfolio_history
