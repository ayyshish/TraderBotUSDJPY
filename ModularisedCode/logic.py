import time
from ib_insync import *
from rsi_calculation import calculate_rsi
from fib_retracement import fib_lines
import pandas as pd
from support_resistance import calculate_support_resistance

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
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='1800 S',
        barSizeSetting='10 secs', whatToShow='MIDPOINT', useRTH=True)
    return pd.DataFrame(bars)

def should_invest(data, support, resistance, fib_levels):
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

    # Check RSI
    if not (min_rsi_allowance <= rsi <= max_rsi_allowance):
        return False

    # Check if resistance is near Fibonacci level
    for res_level in resistance:
        for fib_level in fib_levels.values():
            if abs(res_level - fib_level) / fib_level <= 0.01:  # Within 1% of a Fibonacci level
                return True

    return False

def calculate_stop_loss_take_profit(fib_levels, current_price):
    """
    Calculate the stop loss and take profit levels based on Fibonacci retracement.

    :param fib_levels: Dictionary of Fibonacci levels.
    :param current_price: Current price of the instrument.
    :return: Tuple containing stop loss and take profit levels.
    """
    #TODO: THESE ARE TEMPLATES, NEED TO PROPERLY DO
    stop_loss = current_price - 0.01
    take_profit = current_price + 0.01
    return stop_loss, take_profit

while True:
    current_data = get_latest_data()
    current_data = calculate_rsi(current_data)

    #TODO: change them to not run every minute but every 4h and 30 min / when low high changes respectively
    _, support, resistance = calculate_support_resistance(instrument, duration, bar_size)
    fib_levels, max_price, min_price = fib_lines(current_data)

    if should_invest(current_data, support, resistance, fib_levels):
        stop_loss, take_profit = calculate_stop_loss_take_profit(fib_levels, current_data['close'].iloc[-1])
        print(f"Investing with stop loss at {stop_loss} and take profit at {take_profit}")
        # Implement investment logic here
    else:
        print("Not investing as requirements not met.")
        
    time.sleep(60) # Repeats every 60s