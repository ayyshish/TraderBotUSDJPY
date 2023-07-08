from ib_insync import *
import datetime
import pytz

from sklearn.cluster import KMeans
from matplotlib import pyplot as plt

import mplfinance as mpf

import pandas as pd
import numpy

import pandas_ta as pta
from defs import *

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

instrument = 'USDJPY'
contract = Forex(instrument)
bars = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='30 D',
    barSizeSetting='4 hours', whatToShow='MIDPOINT', useRTH=True)
est = pytz.timezone('US/Eastern')
date_format = "%H:%M"

data = pd.DataFrame(bars)

#number of candles
numCan = len(data.index)

for i in range(numCan):
    if data.at[i,'volume']<0:
        data.at[i,'volume'] = 0

#RSI Append
RSIlength = 14
data["rsi"] = pta.rsi(data['close'], length = RSIlength)
data["rsi"] = data["rsi"].fillna(0)

#Drop Index and reset as date
data.set_index('date', inplace=True, drop=True)

#Create new column 'time'
data["time"] = [d.timestamp() for d in data.index]
data.time = data.time.tz_convert(est)
data = data[["time", "open", "high", "low", "close", "volume", "rsi"]]

#print(data)

lod, hod = 0, 0

lows = pd.DataFrame(data=data, index=data.index, columns=["low"])
highs = pd.DataFrame(data=data, index=data.index, columns=["high"])

low_clusters = get_optimum_clusters(lows)
low_centers = low_clusters.cluster_centers_
low_centers = numpy.sort(low_centers, axis=0)

high_clusters = get_optimum_clusters(highs)
high_centers = high_clusters.cluster_centers_
high_centers = numpy.sort(high_centers, axis=0)

support= []
resistance = []

for low in low_centers[:2]:
    support.append(low[0])

for high in high_centers[-1:]:
    resistance.append(high[0])

data = data[RSIlength:numCan]
ax = plot_stock_data(data, support, resistance)

print(support)
print(resistance)
plt.show()

