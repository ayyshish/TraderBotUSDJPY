from ib_insync import *
import datetime
import pytz

from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import matplotlib.ticker as mpticker
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf

import pandas as pd
import numpy

API_KEY = "1f7b7538ccf25a16531d1289e9685471-6689f6c28c41334cf29e883820550606"
ACCOUNT_ID = "101-003-26247776-001"
OANDA_URL = 'https://api-fxpractice.oanda.com/v3'

SECURE_HEADER = {
    'Authorization': 'Bearer 1f7b7538ccf25a16531d1289e9685471-6689f6c28c41334cf29e883820550606'
}

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

def plot_stock_data(data, support, resistance):
    lines = support + resistance
    s = len(support)
    r = len(resistance)
    redColList = ['#EB6C6B', '#90021F', '#90021F']
    blueColList = ['#7BB4E3', '#006DB2', '#004987']
    colList = createColList(s,r,redColList,blueColList)
    #widthList = (0.5,0.5,1,1,0.5,1)

    style = mpf.make_mpf_style(base_mpf_style='yahoo',y_on_right=False)

    data['Low30'] = 30
    data['High70'] = 70

    ap = [mpf.make_addplot(data['rsi'],color='#ffbd2e', panel=1, ylabel="RSI", ylim=(0,100), width=1),
          mpf.make_addplot(data['Low30'], panel=1, color='#2e70ff', width=0.5),
          mpf.make_addplot(data['High70'], panel=1, color='#2e70ff', width=0.5),]

    mpf.plot(data, type='candle', style=style, title='USDJPY', hlines = dict(hlines=lines, linestyle='--', linewidths=0.8, colors=colList), panel_ratios=(6,2), addplot=ap, returnfig=True)

def mydate(x,pos):
    try:
        est = pytz.timezone('US/Eastern')
        date_format = "%H:%M"
        return datetime.datetime.fromtimestamp(x, tz=est).strftime(date_format)
    except IndexError:
        return ''
    
def createColList(s,r,redColList,blueColList):
    count = (s+r)//3 #assumes 1 resistance and 2 support lines
    bluelist = []
    redlist = []
    for i in range(count):
        redlist.append(redColList[i])
        for j in range(2): #assumes 1 resistance and 2 support lines
            bluelist.append(blueColList[i])
    list = bluelist + redlist
    return list

def SRLines(data, support, resistance):
    lows = pd.DataFrame(data=data, index=data.index, columns=["low"])
    highs = pd.DataFrame(data=data, index=data.index, columns=["high"])

    low_clusters = get_optimum_clusters(lows)
    low_centers = low_clusters.cluster_centers_
    low_centers = numpy.sort(low_centers, axis=0)

    high_clusters = get_optimum_clusters(highs)
    high_centers = high_clusters.cluster_centers_
    high_centers = numpy.sort(high_centers, axis=0)

    for low in low_centers[:2]:
        support.append(low[0])

    for high in high_centers[-1:]:
        resistance.append(high[0])
    
    return support, resistance