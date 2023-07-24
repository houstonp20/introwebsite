from alpaca.trading.client import TradingClient
import alpaca_trade_api as tradeapi
from datetime import datetime
import config

def get_current_price(alpaca_api_key, alpaca_secret_key, base_url, symbol):
    api = tradeapi.REST(alpaca_api_key, alpaca_secret_key, base_url=base_url)
    try:
        quote = api.get_latest_trade(symbol)
        return float(quote.price)

    except tradeapi.rest.APIError as api_error:
        print(f"Error occurred: {api_error}")
        return None

def place_market_order(api_key, secret_key, base_url, ticker, qty, side, type, time_in_force, bracket=False, take_profit=None, stop_loss=None):
    api = tradeapi.REST(api_key, secret_key, base_url=base_url)
    if bracket == True:
        print(f'Take Profit: {take_profit} Stop Loss: {stop_loss}')
        api.submit_order(symbol=ticker,qty=qty,side=side,type=type,time_in_force=time_in_force, order_class='bracket', take_profit={'limit_price': round(take_profit, 2)}, stop_loss={'stop_price': round(stop_loss, 2)})
        order = f"Market order placed: Side: {side} Qty: {qty} Ticker: {ticker} Order type: {type} Time in force: {time_in_force} Take profit: {take_profit} Stop loss: {stop_loss}"
        print(f'Order placed for {ticker}')
    else:
        api.submit_order(symbol=ticker,qty=qty,side=side,type=type,time_in_force=time_in_force)
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
    ph = api.get_portfolio_history(period='1M', timeframe='1D')
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

