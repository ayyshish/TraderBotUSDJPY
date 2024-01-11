import time
from ib_insync import *
from rsi_calculation import calculate_rsi
from fib_retracement import fib_lines
import pandas as pd
from support_resistance import calculate_support_resistance_withdata

# Configuration
instrument = 'USDJPY'
duration = '32 D'
bar_size = '4 hours'
min_rsi_allowance = 30  # Define your RSI minimum
max_rsi_allowance = 70  # Define your RSI maximum

# Initialize IBKR connection
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

def get_latest_data():
    """
    Retrieve the latest data for the specified instrument.
    """
    contract = Forex(instrument)
    bars = ib.reqHistoricalData(contract, endDateTime='', durationStr='30 S', barSizeSetting='1 secs', whatToShow='MIDPOINT', useRTH=True)
    
    return pd.DataFrame(bars)

def should_invest(data, support, resistance, fib_levels, ascending):
    """
    Determine whether to invest based on support, resistance, Fibonacci levels, and RSI.

    :param data: DataFrame with latest price data.
    :param support: List of support levels.
    :param resistance: List of resistance levels.
    :param fib_levels: Dictionary of Fibonacci levels.
    :return: Boolean indicating whether to invest.
    """
    current_price = data['close'].iloc[-1]
    rsi = data['rsi'].iloc[-1]
    sell = False
    buy = False

    # Step 1: Check RSI
    if not (min_rsi_allowance <= rsi <= max_rsi_allowance): #   <- idt this is correct lol
        return False
    
    # Step 2: Check if price is near support or resistance
    for sup_level in support:
        if abs(current_price - sup_level) / sup_level <= 0.005:

            # Check if support is near Fibonacci level and overall trend is upwards
            for fib_level in fib_levels.values():
                if (abs(sup_level - fib_level) / fib_level <= 0.005 and ascending):  # Within 0.5% of a Fibonacci level
                    buy = True
    
    for res_level in resistance:
        if abs(current_price - res_level) / res_level <= 0.005:

            # Check if resistance is near Fibonacci level
            for fib_level in fib_levels.values():
                if (abs(res_level - fib_level) / fib_level <= 0.005 and not ascending):  # Within 0.5% of a Fibonacci level
                    sell = True


    return False

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
    

counter = 0

current_data = get_latest_data()
current_data = calculate_rsi(current_data)

_, support, resistance = calculate_support_resistance_withdata(current_data)
fib_levels, max_price, min_price, ascending = fib_lines(current_data)
print (fib_levels)

while True:

    # call for data every 60s
    current_data = get_latest_data()
    current_data = calculate_rsi(current_data)

    # every 4 hours, recalculate support and resistance and fib lines
    if counter>240:
        counter = 0
        _, support, resistance = calculate_support_resistance_withdata(current_data, instrument, duration, bar_size)
        fib_levels, max_price, min_price, ascending = fib_lines(current_data)

    # check if the newly obtained close price is greater than max or smaller than min. if so, we dont place any trades.
    elif (current_data['close'].iloc[-1] > max_price or current_data['close'].iloc[-1] < min_price):
        counter = 244
        # allow time for price to correct itself, then recalculate support and resistance and fib lines
        time.sleep(120)

    else:

        if should_invest(current_data, support, resistance, fib_levels, ascending):

            stop_loss, take_profit = calculate_stop_loss_take_profit(fib_levels)
            print(f"Investing with stop loss at {stop_loss} and take profit at {take_profit}")

                # Implement investment logic here
                # call to bot to place trade
                
        else:
            print("Not investing as requirements not met.")
        
        time.sleep(60) # Repeats every 60s
    counter += 1