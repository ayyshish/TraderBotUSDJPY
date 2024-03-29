from backtesting import Backtest, Strategy
from rsi_calculation import calculate_rsi
from support_resistance import calculate_support_resistance_withdata
from fib_retracement import fib_lines
from ichimoku_cloud import calc_ichimoku_cloud_signal
from fib_retracement import fib_lines

import pandas as pd
import numpy as np

def calc_fib_lines(data):
    max_price_index = data['close'].idxmax()
    min_price_index = data['close'].idxmin()

    max_price_datetime = data.loc[max_price_index, 'date']
    min_price_datetime = data.loc[min_price_index, 'date']

    ascending = max_price_datetime > min_price_datetime

    max_price = max(data['close'])
    min_price = min(data['close'])
    difference = max_price - min_price

    if ascending:
        fib_levels = [
            round(min_price + (difference * 0.236), 4),
            round(min_price + (difference * 0.382), 4),
            round(min_price + (difference * 0.5), 4),
            round(min_price + (difference * 0.618), 4),
            round(min_price + (difference * 0.764), 4)
        ]
    else:
        fib_levels = [
            round(max_price - (difference * 0.236), 4),
            round(max_price - (difference * 0.382), 4),
            round(max_price - (difference * 0.5), 4),
            round(max_price - (difference * 0.618), 4),
            round(max_price - (difference * 0.764), 4)
        ]   

    return fib_levels

def calculate_stop_loss_take_profit(fib_levels):
    """
    Calculate the stop loss and take profit levels based on Fibonacci retracement.

    :param fib_levels: Dictionary of Fibonacci levels.
    :param current_price: Current price of the instrument.
    :return: Tuple containing stop loss and take profit levels.
    """
    #TODO: THESE ARE TEMPLATES, NEED TO PROPERLY DO

    # Logic: Buy when price between 0.5 and 0.618 levels
    # Overall Downwards trend (Sell): take profit at 0.382 (level5), stop loss at 0.786 (level2)
    # Overall Upwards trend (Buy): take profit at 0.786 (level5) stop loss at 0.382 (level2)

    stop_loss = fib_levels['level2']
    take_profit = fib_levels['level5']
    return stop_loss, take_profit

# Dont Delete 

"""
historical_data = pd.read_pickle("historical_data_excel.pkl")
historical_data = historical_data[["date", "open", "high", "low", "close", "volume"]]
historical_data['date'] = pd.to_datetime(historical_data['date'], format='%Y-%m-%d %H:%M:%S%z')

# Create 'fib_levels' column with NaN values
historical_data['fib_levels'] = np.nan

historical_data = calculate_rsi(historical_data)

start = 0
counter = 30


while counter < len(historical_data):
    max_price = max(historical_data['close'][start:counter])
    min_price = min(historical_data['close'][start:counter])

    # calculate fib levels
    fib_lines_list = calc_fib_lines(historical_data[start:counter])

    # Update fib_levels column with the calculated list
    historical_data.loc[[counter], ['fib_levels']] = historical_data.loc[[counter], ['fib_levels']].applymap(lambda x: fib_lines_list)

    
    start += 1
    counter += 1

historical_data.to_pickle("historical_data_with_fiblines.pkl")
"""
"""
while counter < len(historical_data):
    max_price = max(historical_data['close'][start:counter])
    min_price = min(historical_data['close'][start:counter])

    # calculate fib levels
    _, support_list, resistance_list = calculate_support_resistance_withdata(historical_data[start:counter])

    # Update fib_levels column with the calculated list
    #historical_data['fib_levels'] = historical_data['fib_levels'].apply(lambda x: fib_lines_list if x is np.nan else x)
    historical_data.loc[[counter], ['support']] = historical_data.loc[[counter], ['support']].applymap(lambda x: support_list)
    historical_data.loc[[counter], ['resistance']] = historical_data.loc[[counter], ['resistance']].applymap(lambda x: resistance_list)

    
    start += 1
    counter += 1


# Fill NaN values in 'fib_levels' column with an empty list
# historical_data['fib_levels'] = historical_data['fib_levels'].apply(lambda x: [] if pd.isna(x) else x)

"""

"""
#create a new column 'trade' with 0 as the deafulat value
historical_data['trade'] = 0

start = 31
counter = 61

while counter < len(historical_data):

    #buy condition when rsi<30
    if historical_data['rsi'].iloc[start]<30:

        #check if price is near fib level
        for j in range(len(historical_data['fib_levels'].iloc[start])):
            if abs(historical_data['close'].iloc[start]-historical_data['fib_levels'].iloc[start][j]) <= 0.2:
                
                _, support, resistance = calculate_support_resistance_withdata(historical_data[start:counter].copy())
                print(support)
                print(resistance)

                #_, _, _, ascending = fib_lines(new_df) #check if overall trend is upwards

                #check if support is near fib level and overall trend is upwards
                for sup_level in support:

                    if abs(historical_data['close'].iloc[start]-sup_level) <= 0.2:

                        for fib_level in historical_data['fib_levels'].iloc[start]:

                            if abs(sup_level-fib_level) <= 0.2: # and ascending:
                                historical_data.loc[start, 'trade'] = 1
                                break
    

    start += 1
    counter += 1

    




print(historical_data)
"""

# Ichimoku Cloud Backtest

historical_data = pd.read_pickle("historical_data_excel.pkl")
ichimoku_cloud_backtest = calc_ichimoku_cloud_signal(historical_data)

#drop volume column
ichimoku_cloud_backtest = ichimoku_cloud_backtest.drop(columns=['volume', 'average', 'barCount'])

#create new columns for stop loss and take profit
ichimoku_cloud_backtest.loc[:,'Stop Loss'] = 0
ichimoku_cloud_backtest['Take Profit'] = 0

# calculate stop loss and take profit only for buy signals (1)
buy_signals = ichimoku_cloud_backtest['signal'] == 1.0
buy_data = ichimoku_cloud_backtest.loc[buy_signals]

# check if there are any buy signals before attempting to calculate stop loss and take profit
if not buy_data.empty:

    # extract the buy signals
    buy_indices = buy_data.index

    # loop buy signals
    for buy_index in buy_indices:

        # last 30 rows before buy signal
        start_index = max(0, buy_index - 29)  # Ensure not to go below the first row
        selected_data = historical_data.iloc[start_index:buy_index + 1]

        # Reset the index of historical_data before passing it to fib_lines
        fib_lines_data = fib_lines(selected_data.reset_index(drop=True))

        fib_levels, max_price, min_price, ascending = fib_lines_data
        stop_loss, take_profit = calculate_stop_loss_take_profit(fib_levels)

        ichimoku_cloud_backtest.loc[buy_index, 'Stop Loss'] = stop_loss
        ichimoku_cloud_backtest.loc[buy_index, 'Take Profit'] = take_profit

#change column names
ichimoku_cloud_backtest = ichimoku_cloud_backtest.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', "signal": 'Signal'})
ichimoku_cloud_backtest.index = pd.to_datetime(ichimoku_cloud_backtest['Date'], format='%Y-%m-%d %H:%M:%S%z')
print(ichimoku_cloud_backtest)

class IchimokuCloud(Strategy):

    def init(self):
        pass

    def next(self):
        current_signal = self.data.Signal[-1]

        if current_signal == 1:
            take_profit = self.data['Take Profit'][-1]
            stop_loss = self.data['Stop Loss'][-1]
            price = self.data['Close'][-1]

            # Ensure SL < LIMIT < TP for long orders
            if (stop_loss < price < take_profit):
                self.buy(size=0.01, tp=take_profit, sl=stop_loss)

        elif current_signal == -1:
            if self.position:
                self.position.close()

#We assume a 1:10 margin ratio for a 100,000 USD account
#IBKR charges about 7.83% for a margin loan of >= $100,000
#https://www.interactivebrokers.com.sg/en/trading/margin-rates.php
                
bt = Backtest(ichimoku_cloud_backtest, IchimokuCloud, cash=100000, margin=1/10)

stats = bt.run()
print(stats)
bt.plot()
