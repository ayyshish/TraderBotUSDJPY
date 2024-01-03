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

def plot_stock_data(data, support, resistance, fiblevels, shadeArray):
    lines = support + resistance + fiblevels
    s = len(support)
    r = len(resistance)
    redColList = ['#EB6C6B', '#90021F', '#90021F']
    blueColList = ['#7BB4E3', '#006DB2', '#004987']
    fibColList = ['#FF5733', '#FFA533', '#EEFF33', '#91FF33', '#33FFB0', '#DC33FF', '#FF338A',]
    colList = createColList(s,r,redColList,blueColList, fibColList)

    # Define line and alpha styles for support/resistance lines and fib retracements
    support_resistance_linestyles = ['--' for _ in range(s + r)]
    fib_retracement_linestyles = ['-' for _ in range(len(fibColList))]
    support_resistance_alphas = [1.0 for _ in range(s + r)]
    fib_retracement_alphas = [0.4 for _ in range(len(fibColList))]

    # Combine line styles for all lines
    linestyles = support_resistance_linestyles + fib_retracement_linestyles
    alphas = support_resistance_alphas + fib_retracement_alphas

    style = mpf.make_mpf_style(base_mpf_style='yahoo',y_on_right=False)

    data['Low30'] = 30
    data['High70'] = 70

    ap = [mpf.make_addplot(data['rsi'],color='#ffbd2e', panel=1, ylabel="RSI", ylim=(0,100), width=1),
          mpf.make_addplot(data['Low30'], panel=1, color='#2e70ff', width=0.5),
          mpf.make_addplot(data['High70'], panel=1, color='#2e70ff', width=0.5),]

    mpf.plot(data, type='candle', style=style, title='USDJPY',
                           hlines=dict(hlines=lines, linewidths=0.5, colors=colList, linestyle=linestyles, alpha=alphas), fill_between=shadeArray,
                           panel_ratios=(6, 2), addplot=ap, returnfig=True)


def mydate(x,pos):
    try:
        est = pytz.timezone('US/Eastern')
        date_format = "%H:%M"
        return datetime.datetime.fromtimestamp(x, tz=est).strftime(date_format)
    except IndexError:
        return ''
    
def createColList(s,r,redColList,blueColList, fibColList):
    count = (s+r)//3 #assumes 1 resistance and 2 support lines
    bluelist = []
    redlist = []
    for i in range(count):
        redlist.append(redColList[i])
        for j in range(2): #assumes 1 resistance and 2 support lines
            bluelist.append(blueColList[i])
    list = bluelist + redlist + fibColList
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

def fibLines(data):
    max_price = max(data['close'])
    min_price = min(data['close'])
    difference = max_price - min_price

    level1 = max_price - (difference * 0.236)
    level2 = max_price - (difference * 0.382)
    level3 = max_price - (difference * 0.5)
    level4 = max_price - (difference * 0.618)
    level5 = max_price - (difference * 0.764)

    fibArray = []
    fibArray.append(max_price)
    fibArray.append(level1)
    fibArray.append(level2)
    fibArray.append(level3)
    fibArray.append(level4)
    fibArray.append(level5)
    fibArray.append(min_price)

    #shade areas between fib line
    fb1 = dict(y1=max_price , y2=level1 , alpha=0.2, color='#FFA533')
    fb2 = dict(y1=level1 , y2=level2 , alpha=0.2, color='#EEFF33')
    fb3 = dict(y1=level2 , y2=level3 , alpha=0.2, color='#91FF33')
    fb4 = dict(y1=level3 , y2=level4 , alpha=0.2, color='#33FFB0')
    fb5 = dict(y1=level4 , y2=level5 , alpha=0.2, color='#DC33FF')
    fb6 = dict(y1=level5 , y2=min_price , alpha=0.2, color='#FF338A')
    
    shadeArray = []
    shadeArray.append(fb1)
    shadeArray.append(fb2)
    shadeArray.append(fb3)
    shadeArray.append(fb4)
    shadeArray.append(fb5)
    shadeArray.append(fb6)

    return fibArray, shadeArray
