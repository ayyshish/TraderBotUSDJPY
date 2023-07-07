from ib_insync import *
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

instrument = 'USDJPY'
contract = Forex(instrument)
bars = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='30 D',
    barSizeSetting='4 hours', whatToShow='MIDPOINT', useRTH=True)

# convert to pandas dataframe:
data = pd.DataFrame(bars)

#code to get real time data

mkt_data = ib.reqMktData(contract, '', False, False)
# df_mktdata = util.df(mkt_data)

ib.sleep(2)

# print(df_mktdata)
# print(mkt_data)

def onPendingTicker(tickers):
    print("pending ticker event received")
    print(tickers)

ib.pendingTickersEvent += onPendingTicker

ib.run()