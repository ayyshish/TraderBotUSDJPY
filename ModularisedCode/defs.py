from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

def get_optimum_clusters(df, saturation_point=0.05):
    wcss = []
    k_models = []

    size = min(11, len(df.index))
    for i in range(1, size):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
        kmeans.fit(df)
        wcss.append(kmeans.inertia_)
        k_models.append(kmeans)

    optimum_k = len(wcss)-1
    for i in range(0, len(wcss)-1):
        diff = abs(wcss[i+1] - wcss[i])
        if diff < saturation_point:
            optimum_k = i
            break

    if optimum_k < len(k_models):
        return k_models[optimum_k]
    else:
        raise IndexError("Optimum index is out of range.")

def SRLines(data, support, resistance):
    lows = pd.DataFrame(data=data, index=data.index, columns=["low"])
    highs = pd.DataFrame(data=data, index=data.index, columns=["high"])

    low_clusters = get_optimum_clusters(lows)
    low_centers = low_clusters.cluster_centers_
    low_centers = np.sort(low_centers, axis=0)

    high_clusters = get_optimum_clusters(highs)
    high_centers = high_clusters.cluster_centers_
    high_centers = np.sort(high_centers, axis=0)

    for low in low_centers[:2]:
        support.append(low[0])

    for high in high_centers[-1:]:
        resistance.append(high[0])
    
    return support, resistance
