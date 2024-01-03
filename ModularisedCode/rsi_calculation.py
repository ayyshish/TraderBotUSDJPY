import pandas_ta as pta

def calculate_rsi(data, length=14):
    data['rsi'] = pta.rsi(data['close'], length=length)
    data['rsi'] = data['rsi'].fillna(0)
    return data