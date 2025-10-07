import numpy as np
import geopandas as gpd
from shapely.geometry import Point

def sigmoid(distance, threshold, k=None):
    k = k or (threshold / 4)
    return 1 / (1 + np.exp((distance - threshold) / k))

def category_score(user_point, gdf, category, threshold):
    subset = gdf[gdf["category"] == category]
    if subset.empty:
        return 0.0
    nearest = subset.distance(user_point).min()
    return sigmoid(nearest, threshold)

def overall_score(user_lat, user_lon, categories, thresholds, gdf, weights=None):
    user_point = Point(user_lon, user_lat)
    weights = weights or {c: 1 for c in categories}
    scores = {}
    for c in categories:
        s = category_score(user_point, gdf, c, thresholds[c])
        scores[c] = s
    total = sum(weights[c]*scores[c] for c in categories) / sum(weights.values())
    return total, scores
