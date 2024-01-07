from ib_insync import *
import pandas as pd
from defs import *

def calculate_support_resistance(instrument, duration, bar_size, show_type='MIDPOINT'):
    """
    Connect to IBKR, retrieve historical data for the given instrument, and calculate support and resistance lines.

    :param instrument: The instrument to retrieve data for (e.g., 'USDJPY').
    :param duration: Duration for historical data (e.g., '32 D').
    :param bar_size: Bar size setting (e.g., '4 hours').
    :param show_type: What to show in historical data (e.g., 'MIDPOINT').
    :return: DataFrame with historical data and lists of support and resistance levels.
    """
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=1)

    contract = Forex(instrument)
    
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr=duration,
        barSizeSetting=bar_size, whatToShow=show_type, useRTH=True)

    data = pd.DataFrame(bars)

    support, resistance = SRLines(data, [], [])
    return data, support, resistance

def calculate_support_resistance_withdata(current_data):
  
    data = current_data

    support, resistance = SRLines(data, [], [])
    #print("Support levels:", support)
    #print("Resistance levels:", resistance)
    return data, support, resistance

# if __name__ == "__main__":
#     # Example usage
#     data, support, resistance = calculate_support_resistance('USDJPY', '32 D', '4 hours')
#     print("Support levels:", support)
#     print("Resistance levels:", resistance)