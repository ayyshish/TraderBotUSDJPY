import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
from ib_insync import *


# Configuration
instrument = 'USDJPY'
duration = '100 D'
bar_size = '4 hours'

# Initialize IBKR connection
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

contract = Forex(instrument)
data = pd.DataFrame(ib.reqHistoricalData(contract, endDateTime='', durationStr=duration, barSizeSetting=bar_size, whatToShow='MIDPOINT', useRTH=True))
historical_data = data[["date", "open", "high", "low", "close"]]

def calc_ichimoku_cloud(data):

    """
    Calculate the Ichimoku Cloud values for the given data.

    :param data: DataFrame with latest price data.
    :return: DataFrame with Ichimoku Cloud values.
    """


    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    nine_period_high = data['high'].rolling(window=9).max()
    nine_period_low = data['low'].rolling(window=9).min()
    data.loc[:,'tenkan_sen'] = (nine_period_high + nine_period_low) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = data['high'].rolling(window=26).max()
    period26_low = data['low'].rolling(window=26).min()
    data.loc[:,'kijun_sen'] = (period26_high + period26_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(26)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = data['high'].rolling(window=52).max()
    period52_low = data['low'].rolling(window=52).min()
    data['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)

    # The most current closing price plotted 22 time periods behind
    data['chikou_span'] = data['close'].shift(-22)

    # Create 'cloud_colour' column with NaN values
    data['cloud_colour'] = np.nan

    # If Senkou Span A > Senkou Span B and Chikou Span > Senkou Span A, cloud_colour = green
    # If Senkou Span A < Senkou Span B and Chikou Span < Senkou Span A, cloud_colour = red
    # Else, cloud_colour = grey
    for index, row in data.iterrows():
        if row['senkou_span_a'] > row['senkou_span_b'] and row['chikou_span'] > row['senkou_span_a']:
            data.loc[index, 'cloud_colour'] = 'green'
        elif row['senkou_span_a'] < row['senkou_span_b'] and row['chikou_span'] < row['senkou_span_a']:
            data.loc[index, 'cloud_colour'] = 'red'
        else:
            data.loc[index, 'cloud_colour'] = 'grey'
    
    #print(data)

    return data

def kumo_cloud_plot(data):
    span = [mpf.make_addplot(data['senkou_span_a'], color='green'),
            mpf.make_addplot(data['senkou_span_b'], color='red'),
            mpf.make_addplot(data['chikou_span'], color='blue'),
            mpf.make_addplot(data['tenkan_sen'], color='orange'),
            mpf.make_addplot(data['kijun_sen'], color='purple')

    ]
    
    mpf.plot(data, type='candle', addplot=span, fill_between = dict(y1=data['senkou_span_a'].values, y2=data['senkou_span_b'].values, alpha = 0.2), style='yahoo', title='Ichimoku Cloud', ylabel='Price (JPY)', ylabel_lower='Volume', figscale=1.5)


def calc_ichimoku_cloud_signal(data):
    """
    Calculate the Ichimoku Cloud signal for the given data.

    :param data: DataFrame with latest price data.
    :return: True if signal is buy, False if signal is sell, None if no signal.
    """

    # Buy conditions
    # 1. Price > Senkou Span A anf Senkou Span B
    # 2. Price > kijun sen
    # 3. tenkan sen > kijun sen

    # Sell conditions
    # 1. Price < Senkou Span A and Senkou Span B
    # 2. Price < kijun sen
    # 3. tenkan sen < kijun sen

    buy = False
    sell = False

    data = calc_ichimoku_cloud(data)

    span_max = data[['senkou_span_a', 'senkou_span_b']].max(axis=1)
    span_min = data[['senkou_span_a', 'senkou_span_b']].min(axis=1)
    data['cloud_top'] = span_max
    data['cloud_bottom'] = span_min

    signal = np.where(
        ((data['close'] > data['cloud_top']) & (data['close'] > data['kijun_sen']) & (data['tenkan_sen'] > data['kijun_sen'])), 1.0,  # buy

        np.where(
            ((data['close'] <= data['cloud_bottom']) & (data['close'] <= data['kijun_sen']) & (data['tenkan_sen'] <= data['kijun_sen'])), -1.0, #sell
             
            0.0)) # do nothing
    
    data['signal'] = signal
    data.drop(['senkou_span_a', 'senkou_span_b', 'chikou_span', 'tenkan_sen', 'kijun_sen', 'cloud_colour', 'cloud_top', 'cloud_bottom'], axis=1, inplace=True)
    return data
    


print(historical_data)

cloud = calc_ichimoku_cloud_signal(historical_data)
print(cloud)
cloud.index = pd.to_datetime(cloud['date'], format='%Y-%m-%d %H:%M:%S%z')
#kumo_cloud_plot(cloud)
