def fib_lines(data):

    max_price_index = data['close'].idxmax()
    min_price_index = data['close'].idxmin()

    max_price_datetime = data.iloc[max_price_index, 0]
    min_price_datetime = data.iloc[min_price_index, 0]

    ascending = max_price_datetime > min_price_datetime

    max_price = max(data['close'])
    min_price = min(data['close'])
    difference = max_price - min_price

    if ascending:
        fib_levels = {
            'level1': min_price + (difference * 0.236),
            'level2': min_price + (difference * 0.382),
            'level3': min_price + (difference * 0.5),
            'level4': min_price + (difference * 0.618),
            'level5': min_price + (difference * 0.764)
        }
    else:
        fib_levels = {
            'level5': max_price - (difference * 0.236),
            'level4': max_price - (difference * 0.382),
            'level3': max_price - (difference * 0.5),
            'level2': max_price - (difference * 0.618),
            'level1': max_price - (difference * 0.764)
        }   

    return fib_levels, max_price, min_price, ascending