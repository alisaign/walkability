import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# --- Scoring helper ---
def sigmoid(distance, threshold, k=None):
    k = k or (threshold / 4)
    return 1 / (1 + np.exp((distance - threshold) / k))

def category_score(user_point, gdf, category, threshold):
    subset = gdf[gdf["category"] == category]
    if subset.empty:
        return 0.0
    nearest = subset.distance(user_point).min()
    return sigmoid(nearest, threshold)

# --- Filtering helper ---
def get_nearby_points(user_point, gdf, category, threshold):
    """Return POIs of this category within threshold radius."""
    subset = gdf[gdf["category"] == category]
    if subset.empty:
        return gpd.GeoDataFrame(columns=gdf.columns)
    subset["dist"] = subset.geometry.distance(user_point)
    return subset[subset["dist"] <= threshold]

# --- Aggregation helper ---
def combine_scores(breakdown):
    """Weighted average of all category scores."""
    total_w = sum(r["weight"] for r in breakdown)
    if not total_w:
        return 0
    weighted_sum = sum(r["score"] * r["weight"] for r in breakdown)
    return round(100 * weighted_sum / total_w, 1)

# --- Main orchestrator ---
def analyze_walkability(user_lat, user_lon, thresholds, weights, gdf):
    """Compute walkability index for a given location."""
    user_point = Point(user_lon, user_lat)
    breakdown, nearby_points = [], []

    for category, threshold in thresholds.items():
        score = category_score(user_point, gdf, category, threshold)
        nearby = get_nearby_points(user_point, gdf, category, threshold)
        w = weights.get(category, 1)
        breakdown.append({"name": category, "score": score, "weight": w})
        nearby_points.extend(nearby.to_dict("records"))

    index = combine_scores(breakdown)
    return {"index": index, "breakdown": breakdown, "nearby": nearby_points}
