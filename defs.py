from ib_insync import *
import datetime
import pytz

from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import matplotlib.ticker as mpticker
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf

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
    style = mpf.make_mpf_style(base_mpf_style='yahoo',y_on_right=False)

    data['Low30'] = 30
    data['High70'] = 70

    ap = [mpf.make_addplot(data['rsi'],color='#ffd300', panel=1, ylabel="RSI", ylim=(0,100)),
          mpf.make_addplot(data['Low30'], panel=1, color='#e3c565'),
          mpf.make_addplot(data['High70'], panel=1, color='#d6b85a'),]

    mpf.plot(data, type='candle', style=style, title='USDJPY', hlines = dict(hlines=lines, linestyle='--', linewidths=1, colors='#0F52Ba'), panel_ratios=(6,2), addplot=ap, returnfig=True)

def mydate(x,pos):
    try:
        est = pytz.timezone('US/Eastern')
        date_format = "%H:%M"
        return datetime.datetime.fromtimestamp(x, tz=est).strftime(date_format)
    except IndexError:
        return ''