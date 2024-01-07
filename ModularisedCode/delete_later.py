import pandas as pd

historical_data = pd.read_pickle("historical_data_with_fiblines.pkl")\

#slice first 30 columns
historical_data = historical_data[31:]

#find object type of column 'fib_levels'
print(type(historical_data['fib_levels'][31]))

print(historical_data)



