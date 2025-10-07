import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# --- Scoring helper ---
def sigmoid(distance, threshold, k=None):
    """Smoothly decreases score with distance."""
    k = k or (threshold / 4)
    return 1 / (1 + np.exp((distance - threshold) / k))


def category_score(user_point, gdf, category, threshold):
    """Return score (0–1) for the nearest POI of this category."""
    subset = gdf[gdf["category"] == category]
    if subset.empty:
        return 0.0

    # compute nearest distance
    nearest = subset.geometry.distance(user_point).min()
    return float(sigmoid(nearest, threshold))


# --- Filtering helper ---
def get_nearby_points(user_point, gdf, category, threshold):
    """Return POIs of this category within threshold radius."""
    subset = gdf[gdf["category"] == category].copy()
    if subset.empty:
        return []

    subset["dist"] = subset.geometry.distance(user_point)
    nearby = subset[subset["dist"] <= threshold]

    # Return only useful fields for frontend (smaller payload)
    return [
        {
            "category": category,
            "name": row.get("stop_name") or row.get("name") or category,
            "geometry": row["geometry"].__geo_interface__  # GeoJSON-style geometry
        }
        for _, row in nearby.iterrows()
    ]


# --- Aggregation helper ---
def combine_scores(breakdown):
    """Weighted average of all category scores (0–100)."""
    total_w = sum(r["weight"] for r in breakdown)
    if not total_w:
        return 0.0
    weighted_sum = sum(r["score"] * r["weight"] for r in breakdown)
    return round(100 * weighted_sum / total_w, 1)


# --- Main orchestrator ---
def analyze_walkability(user_lat, user_lon, thresholds, weights, gdf):
    """Compute walkability index and nearby POIs."""
    user_point = Point(user_lon, user_lat)
    breakdown, all_nearby = [], []

    for category, threshold in thresholds.items():
        # compute per-category score
        score = category_score(user_point, gdf, category, threshold)

        # find nearby POIs for display
        nearby = get_nearby_points(user_point, gdf, category, threshold)

        # record weighted info
        w = float(weights.get(category, 1))
        breakdown.append({"name": category, "score": score, "weight": w})

        # extend nearby points
        all_nearby.extend(nearby)

    # combine overall index
    index = combine_scores(breakdown)

    # return full payload expected by frontend
    return {
        "center": {"lat": user_lat, "lon": user_lon},
        "index": index,
        "breakdown": breakdown,
        "buffers_m": list(thresholds.values()),  # optional for map circles
        "nearby": all_nearby
    }
