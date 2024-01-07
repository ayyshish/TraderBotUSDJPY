from time import sleep
from ib_insync import *
from datetime import datetime
import pandas as pd
import pytz

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

instrument = 'USDJPY'
contract = Forex(instrument)

end_date = '20231201'
duration_str = '30 D'
bar_size_setting = '4 hours'
what_to_show = 'MIDPOINT'
use_rth = True

# Initialize an empty list to store individual DataFrames
all_data = []

while pd.to_datetime(end_date) > pd.to_datetime('20050601'):  # Change the end date accordingly
    # Format the endDateTime in the required format
    end_date_str = end_date + " 00:00:00"+ " US/Eastern"
    print(end_date_str)

    # Make a request for historical data
    bars = ib.reqHistoricalData(
        contract, endDateTime=end_date_str, durationStr=duration_str,
        barSizeSetting=bar_size_setting, whatToShow=what_to_show, useRTH=use_rth)

    if bars:
        # Convert the bars data to a DataFrame and append to the list
        data = util.df(bars)
        all_data.append(data)

        # Update end date for the next request
        end_datetime_object = data.iloc[0]['date']
        end_datetime = datetime.strptime(str(end_datetime_object), "%Y-%m-%d %H:%M:%S%z")
        end_date = end_datetime.strftime("%Y%m%d")

        print("End date:", end_date)    
        print("Success")

    sleep(2)

# Concatenate all DataFrames in the list into a single DataFrame
complete_data = pd.concat(all_data, ignore_index=True)
complete_data['date'] = complete_data['date'].astype(str)
print(complete_data)

ib.disconnect()

# Now, 'complete_data' contains all the historical market data in one DataFrame

# Store the complete_data DataFrame in an Excel file
complete_data.to_pickle("historical_data_excel.pkl")
try:
    complete_data.to_excel("historical_data_excel.xlsx", index=False)
    print("Data has been successfully saved")
except Exception as e: 
    print(f"Error saving data to Excel: {e}")