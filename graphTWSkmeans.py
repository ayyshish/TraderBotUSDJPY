from ib_insync import *
import datetime
import pytz

from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import matplotlib.ticker as mpticker
from mplfinance.original_flavor import candlestick_ohlc

import pandas as pd
import numpy

def get_optimum_clusters(df):
    '''

    :param df: dataframe
    :param saturation_point: The amount of difference we are willing to detect
    :return: clusters with optimum K centers

    This method uses elbow method to find the optimum number of K clusters
    We initialize different K-means with 1..10 centers and compare the inertias
    If the difference is no more than saturation_point, we choose that as K and move on
    '''
    saturation_point = 0.05
    wcss = []
    k_models = []

    size = min(11, len(df.index))
    for i in range(1, size):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
        kmeans.fit(df)
        wcss.append(kmeans.inertia_)
        k_models.append(kmeans)

    # Compare differences in inertias until it's no more than saturation_point
    optimum_k = len(wcss)-1
    for i in range(0, len(wcss)-1):
        diff = abs(wcss[i+1] - wcss[i])
        if diff < saturation_point:
            optimum_k = i
            break
    
    '''
    print(df)
    print("Optimum K is " + str(optimum_k + 1))
    print(optimum_k)
    print(len(k_models))
    '''

    # Check if optimum_k is within the range of k_models
    if optimum_k < len(k_models):
        optimum_clusters = k_models[optimum_k]
        return optimum_clusters
    else:
        # Handle the case when the index is out of range
        raise IndexError("Optimum index is out of range. Please check the data or adjust the range.")


def plot_stock_data(data):
    fig, ax = plt.subplots()
    ax1 = plt.subplot2grid((5,1), (0,0), rowspan=4)
    ax2 = plt.subplot2grid((5,1), (4,0), sharex=ax1)

    ax1.set_title("{}".format(instrument))
    ax1.set_facecolor("#131722")
    ax1.xaxis.set_major_formatter(mpticker.FuncFormatter(mydate))

    candlestick_ohlc(ax1, data.to_numpy(), width=8, colorup='#77d879', colordown='#db3f3f')

    ax2.bar(data['time'], 1, width=30)
    ax2.xaxis.set_major_formatter(mpticker.FuncFormatter(mydate))
    fig.subplots_adjust(hspace=0)
    fig.autofmt_xdate()
    return ax1


def mydate(x,pos):
    try:
        return datetime.datetime.fromtimestamp(x, tz=est).strftime(date_format)
    except IndexError:
        return ''

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

data.set_index('date', inplace=True, drop=True)

print(data)

data["time"] = [d.timestamp() for d in data.index]
data.time = data.time.tz_convert(est)
data = data[["time", "open", "high", "low", "close", "volume"]]

print(data)

ax = plot_stock_data(data)

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
    ax.axhline(low[0], color='yellow', ls='--')
    support.append(low[0])

for high in high_centers[-1:]:
    ax.axhline(high[0], color='orange', ls='--')
    resistance.append(high[0])

print(support)
print(resistance)
plt.show()

