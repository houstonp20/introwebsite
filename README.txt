This is my introduction website. It includes some basic information about myself and some contact methods. Also, 
one of the pages I set up to display the results of a trading algorithm I built. Most of the work done on this repo
has been for this, so I will summarize it briefly.

* trading-algorithm.html
This is the results page for a very basic trading algorithm I built using Python to access Yahoo Finance market-data using their API and make trades based off of that information using Alpaca's paper-trading API. I will provide a brief summary of how it 
works here with more explanation of the actual logic below, but you can check it out for yourself in the Backend folder in the python files. 

Step 1: The data_collections file is called. This makes a call to the yfinance API to get the market data of every stock in my 'stocks' list. It then calculates the stochastic oscillator and 20 and 50 day Simple Moving Averages for each stock. It returns those as a dataframe with columns for the indicators and the price data. 

Step 2: The trading_decisions file is called. It runs a function to check whether the signal is bullish, bearish, or neither. Next, it 
checks proximity to fibonacci numbers to decide whether a signal should be acted upon. It then returns a dataframe with 'Hold', 'Buy', 
or 'Sell' signals for each stock.

Step 3: The app file iterates through each stock to check its signal, whether it confirms or denies my position, and whether I have enough 
buying power to act upon it. Information about any orders placed or hold signals received are appended to a list that is reset every 
time the algorithm is run and the list is returned as the output.

Step 4: The account file is called. The list from the previous step is inserted into an sqlite3 database stored locally in a table called 
'alpaca_signals'. My open positions are stored into a table called 'alpaca_positions', and my portfolio equity and profit/loss
history are stored in a table called 'portfolio_history'.

Step 5: The tables are then written into json form and, using github's API, their contents are stored in my repo in .json files. 

Step 6: The javascript on my trading-algorithm.html file creates a table for the positions and signals, and a chart for the 
profit/loss and equity.

* Algorithm Logic
This is essentially a pure trend strategy with a medium-range timespan in mind, as I can only placa certain amount of API 
calls and Polygon only carries day-end data. I was more focused on the actual process of building an algorithm than I was on 
implementing an extremely complex strategy. That being said, there is some depth to it.

Step 1: The Simple Moving Averages of the stock being examined are compared. The logic tests to see if the last value of the 20 day SMA 
is lower or higher than the last vale of the 50 day SMA. It then checks to see if the 20 day was also lower or higher than 
the 50 day 10 days ago. If it is, it is given a value of 'strong positive/negative'. If not, it is 'new positive/negative'.

Step 2: The Stochastic Oscillator lines are compared to see if an intersection has occurred. If it has, it tests whether or not 
the intersection occurred above or below our thresholds (I set them to 20 and 80). Another value is assigned 'Bullish/Bearish intersection
above/below threshold' if applicable. Otherwise, another value of 'No signal' is assigned. So the algorithm requires a stochasitc 
oscillator intersection to actually place orders.

Step 3: Fibonacci numbers are calcualated for both an extension and a retracement of the stock. If the signal from earlier is just a 
'Bullish/Bearish Intersection' and not above/below a threshold, we check to see whether it is near a fibonacci retracement number 
if the value from earlier is 'strong negative' or near a fibonacci extension number if the value is 'strong positive'. If it is, the signal 
is 'Buy' or 'Sell' If the value is a 'new' negative or positive, we hold. If the intersection occurs outside of our thresholds, the signal 
is 'Buy' or 'Sell', regardless of fibonacci numbers. 

Step 4: For each signal, if the signal indicates 'Buy', we don't have a position (checked through a function) and we have enough buying 
power, we buy $5000 worth of shares, rounded down to the nearest share. The take profit is %10 and the stop-loss is %90 of the current price. 
If we have a position and it is long, we hold. If we have a position and it is short, we place a sell order for the amount of shares we hold.
If the signal indicates 'Sell', we don't have a position, and we have enough buying power, we place a short order with the same argument for 
quanity, but the take profit is 90% of the current price and stop loss is a 10% increase in price.
