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
    contract, endDateTime='', durationStr='32 D', #2 days more than needed to accomodate RSI
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
RSIlength = 14 #candles (periods)
data["rsi"] = pta.rsi(data['close'], length = RSIlength)
data["rsi"] = data["rsi"].fillna(0)

#Drop Index and reset as date
data.set_index('date', inplace=True, drop=True)

#Create new column 'time'
data["time"] = [d.timestamp() for d in data.index]
data.time = data.time.tz_convert(est)
data = data[["time", "open", "high", "low", "close", "volume", "rsi"]]

#print(data)

#Finding supp resistance lines for diff timeframes
#At 4hr candles -> 1day = 7candles
#lod, hod = 0, 0

support= []
resistance = []

support, resistance = SRLines(data, support, resistance)
support, resistance = SRLines(data[-7:], support, resistance) #getting last 7 candles (1day 4hr)

data = data[RSIlength:numCan]
fiblevels, shadeArray = fibLines(data)
ax = plot_stock_data(data, support, resistance, fiblevels, shadeArray)

#print(support)
#print(resistance)
plt.show()