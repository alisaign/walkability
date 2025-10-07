"""
Walkability scoring and nearby-points logic.

Provides category-based scoring, filtering, and aggregation for
walkability analysis. Distances are computed in meters using EPSG:32188
(local projection for Montréal).
"""

import logging
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# --- configure logger once for the whole module ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s:%(funcName)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# --- constants ---
LOCAL_EPSG = 32188  # NAD83 / MTM zone 8 for Montréal

# --- helpers ---
def sigmoid(distance, threshold, k=None):
    """Smoothly decrease score with distance."""
    k = k or (threshold / 4)
    return 1 / (1 + np.exp((distance - threshold) / k))


def category_score(user_point, gdf, category, threshold):
    """Return a 0–1 score for nearest POI of given category."""
    subset = gdf[gdf["category"] == category]
    if subset.empty:
        logger.debug(f"{category}: no data")
        return 0.0

    # project both to meters
    subset_m = subset.to_crs(epsg=LOCAL_EPSG)
    user_point_m = gpd.GeoSeries([user_point], crs=4326).to_crs(epsg=LOCAL_EPSG).iloc[0]

    nearest = subset_m.geometry.distance(user_point_m).min()
    score = float(sigmoid(nearest, threshold))
    logger.info(f"{category}: nearest={nearest:.1f} m  score={score:.3f}")
    return score


def get_nearby_points(user_point, gdf, category, threshold):
    """Return list of POIs within threshold meters of user_point."""
    subset = gdf[gdf["category"] == category].copy()
    if subset.empty:
        logger.debug(f"{category}: no nearby candidates")
        return []

    # project to metric CRS for distance
    subset_m = subset.to_crs(epsg=LOCAL_EPSG)
    user_point_m = gpd.GeoSeries([user_point], crs=4326).to_crs(epsg=LOCAL_EPSG).iloc[0]

    subset_m["dist"] = subset_m.geometry.distance(user_point_m)
    nearby = subset_m[subset_m["dist"] <= threshold]

    # convert back to geographic CRS (lat/lon) for Leaflet
    nearby_geo = nearby.to_crs(epsg=4326)

    results = [
        {
            "category": category,
            "name": row.get("stop_name") or row.get("name") or category,
            "geometry": row["geometry"].__geo_interface__
        }
        for _, row in nearby_geo.iterrows()
    ]
    logger.info(f"{category}: {len(results)} nearby features ≤ {threshold} m")
    return results



def combine_scores(breakdown):
    """Weighted mean of category scores (0–100)."""
    total_w = sum(r["weight"] for r in breakdown)
    if not total_w:
        return 0.0
    weighted_sum = sum(r["score"] * r["weight"] for r in breakdown)
    index = round(100 * weighted_sum / total_w, 1)
    logger.info(f"Combined index={index}")
    return index


def analyze_walkability(location, user_lat, user_lon, thresholds, weights, gdf):
    """Compute overall walkability index and nearby POIs."""
    logger.info(f"Analyzing walkability for lat={user_lat}, lon={user_lon}")
    user_point = Point(user_lon, user_lat)
    breakdown, all_nearby = [], []

    for category, threshold in thresholds.items():
        score = category_score(user_point, gdf, category, threshold)
        nearby = get_nearby_points(user_point, gdf, category, threshold)
        w = float(weights.get(category, 1))
        breakdown.append({"name": category, "score": score, "weight": w})
        all_nearby.extend(nearby)

    index = combine_scores(breakdown)

    result = {
        "location": location,
        "center": {"lat": user_lat, "lon": user_lon},
        "index": index,
        "breakdown": breakdown,
        "buffers_m": list(thresholds.values()),
        "nearby": all_nearby,
    }
    logger.info(f"Analysis complete: {len(all_nearby)} total nearby POIs")
    return result
