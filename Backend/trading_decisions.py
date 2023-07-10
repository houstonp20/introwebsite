import pandas as pd
import data_collection
import numpy as np






def check_proximity_to_fib(stock_data, stock, fib_df, trend):
    print("Calculating Fibonacci Numbers")
    if trend == 'negative':
        for value in fib_df[f'{stock} Retracement Lines:']:
            if abs(stock_data[f'{stock} close'].iloc[-1] - value) <= (stock_data[f'{stock} close'].iloc[-1] * 0.05):
                return True
            return False
    elif trend == 'positive':
        for value in fib_df[f'{stock} Extension Lines:']:
            if abs(stock_data[f'{stock} close'].iloc[-1] - value) <= (stock_data[f'{stock} close'].iloc[-1] * 0.05):
                    return True
            return False
        

def check_stochastic_intersections_and_SMA(stock_data, stocks):
    print("Checking Indicator Signals")
    signals = []
    trend_df = pd.DataFrame()
    for stock in stocks:
        rolling_mean_20day = stock_data[f'{stock} 20 day SMA'].rolling(window=10).mean()
        rolling_mean_50day = stock_data[f'{stock} 50 day SMA'].rolling(window=10).mean()
        if stock_data[f'{stock} 20 day SMA'].iloc[-1] < stock_data[f'{stock} 50 day SMA'].iloc[-1]:
            if (rolling_mean_20day.iloc[-10:] < rolling_mean_50day.iloc[-10:]).all():
                trend_df.loc[0, f'{stock} trend'] = 'strong negative'
            else: trend_df.loc[0, f'{stock} trend'] = 'new negative'
        if stock_data[f'{stock} 20 day SMA'].iloc[-1] > stock_data[f'{stock} 50 day SMA'].iloc[-1]:
            if (rolling_mean_20day.iloc[-10:] > rolling_mean_50day.iloc[-10:]).all():
                trend_df.loc[0, f'{stock} trend'] = 'strong positive'
            else:
                trend_df.loc[0, f'{stock} trend'] = 'new positive'
        if stock_data[f'{stock} Stochastic Oscillator K'].iloc[-1] > stock_data[f'{stock} Stochastic Oscillator D'].iloc[-1] and \
                    stock_data[f'{stock} Stochastic Oscillator K'].iloc[-2] < stock_data[f'{stock} Stochastic Oscillator D'].iloc[-2]:
            if stock_data[f'{stock} Stochastic Oscillator K'].iloc[-1] < 20:
                    signal = f'{stock} Bullish Intersection Below Threshold'
                    signals.append(f'{signal}')
            else: 
                    signal = f'{stock} Bullish Intersection'
                    signals.append(f'{signal}')
        elif stock_data[f'{stock} Stochastic Oscillator K'].iloc[-1] < stock_data[f'{stock} Stochastic Oscillator D'].iloc[-1] and \
                    stock_data[f'{stock} Stochastic Oscillator K'].iloc[-2] > stock_data[f'{stock} Stochastic Oscillator D'].iloc[-2]:
            if stock_data[f'{stock} Stochastic Oscillator K'].iloc[-1] > 80:
                    signal = f'{stock} Bearish Intersection Above Threshold'
                    signals.append(f'{signal}')
            else:
                    signal = f'{stock} Bearish Intersection'
                    signals.append(f'{signal}')
        else:
            signal = f'{stock} No signal'
            signals.append(signal)
    return signals, trend_df

def calculate_fib_numbers(stocks, stock_data):
    fib_df = pd.DataFrame()
    for stock in stocks:
        low = stock_data[f'{stock} close'].min()
        high = stock_data[f'{stock} close'].max()
        diff = high - low
        fib2618 = high + (diff * 2.618)
        fib2000 = high + (diff * 2)
        fib1618 = high + (diff * 1.618)
        fib1382 = high + (diff * 1.382)
        fib1000 = high + (diff * 1)
        fib618 = high + (diff * 0.618)
        fib100 = high
        fib764 = low + (diff*0.764)
        fib_r_618 = low + (diff*0.618)
        fib50 = low + (diff*0.5)
        fib382 = low + (diff*0.382)
        fib286 = low + (diff*0.286)
        fib_extension = [fib2618, fib2000, fib1618, fib1382, fib1000, fib618]
        fib_retracement = [fib100, fib764, fib_r_618, fib50, fib382, fib286]
        fib_df[f'{stock} Extension Lines:'] = fib_extension
        fib_df[f'{stock} Retracement Lines:'] = fib_retracement
    return fib_df


def check_signals(stock_data, stocks, signals, trend_df, fib_df):
    output_df = pd.DataFrame()
    for stock in stocks:
            for signal in signals:
                if signal == f'{stock} Bullish Intersection':
                    if trend_df.loc[0, f'{stock} trend'] == 'strong negative':
                        fib = check_proximity_to_fib(stock_data, stock, fib_df, 'negative')
                        if fib == True:
                            output_df.loc[0, f'{stock}'] = 'Buy'
                        else:
                            output_df.loc[0, f'{stock}'] = 'Hold'
                    elif trend_df.loc[0, f'{stock} trend'] == 'new negative':
                        output_df.loc[0, f'{stock}'] = 'Hold'
                    elif trend_df.loc[0, f'{stock} trend'] == 'new positive' or trend_df.loc[0, f'{stock} trend'] == 'strong positive':
                        output_df.loc[0, f'{stock}'] = 'Hold'
                elif signal == f'{stock} Bullish Intersection Below Threshold':
                    output_df.loc[0, f'{stock}'] = 'Buy'
                elif signal == f'{stock} Bearish Intersection':
                    if trend_df.loc[0, f'{stock} trend'] == 'strong positive':
                        fib = check_proximity_to_fib(stock_data, stock, fib_df, 'negative')
                        if fib == True:
                            output_df.loc[0, f'{stock}'] = 'Sell'
                        else:
                            output_df.loc[0, f'{stock}'] = 'Hold'
                    elif trend_df.loc[0, f'{stock} trend'] == 'new positive':
                        output_df.loc[0, f'{stock}'] = 'Hold'
                    elif trend_df.loc[0, f'{stock} trend'] == 'new negative' or trend_df.loc[0, f'{stock} trend'] == 'strong negative':
                        output_df.loc[0, f'{stock}'] = 'Hold'
                elif signal == f'{stock} Bearish Intersection Above Threshold':
                    output_df.loc[0, f'{stock}'] = 'Sell'
                elif signal == f'{stock} No signal':
                     output_df.loc[0, f'{stock}'] = 'Hold'
    return output_df

                    
                        
