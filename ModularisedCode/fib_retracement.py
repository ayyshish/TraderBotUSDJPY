def fib_lines(data):
    max_price = max(data['high'])
    min_price = min(data['low'])
    difference = max_price - min_price

    fib_levels = {
        'level1': max_price - (difference * 0.236),
        'level2': max_price - (difference * 0.382),
        'level3': max_price - (difference * 0.5),
        'level4': max_price - (difference * 0.618),
        'level5': max_price - (difference * 0.764)
    }

    return fib_levels, max_price, min_price