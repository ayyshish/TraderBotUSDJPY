from ib_insync import *
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

instrument = 'USDJPY'
contract = Forex(instrument)

#code to get real time data
mkt_data = ib.reqMktData(contract, '', False, False)

ib.sleep(2)

def onPendingTicker(tickers):
    print("Pending ticker event received: ")
    print(tickers)

ib.pendingTickersEvent += onPendingTicker

ib.run()

#Example of ouput:
'''
Pending ticker event received:
{Ticker(contract=Forex('USDJPY', exchange='IDEALPRO'), time=datetime.datetime(2023, 7, 8, 17, 16, 35, 811976, 
tzinfo=datetime.timezone.utc), minTick=0.001, bid=-1.0, bidSize=0.0, ask=-1.0, askSize=0.0, high=144.195, low=142.07, close=144.07, 
halted=0.0, ticks=[TickData(time=datetime.datetime(2023, 7, 8, 17, 16, 35, 811976, tzinfo=datetime.timezone.utc), 
tickType=49, price=0.0, size=0)])}
'''
#Clean above feed to usable data