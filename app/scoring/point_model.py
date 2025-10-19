"""

"""

import logging
import geopandas as gpd
from shapely.geometry import Point

from app.scoring.utils import (
    convert_to_geo_crs,
    convert_to_metric_crs,
    linear_decay,
    combine_scores,
)

logger = logging.getLogger(__name__)



def calculate_category_score(user_point: Point, pois_m: gpd.GeoDataFrame, category: str, threshold: float):
    """Calculate a 0-1 score for given category."""
    subset_m = pois_m[pois_m["category"] == category]
    nearest = float(subset_m["distance"].min())
    score = linear_decay(nearest, threshold)
    logger.info(f"{category}: nearest={nearest:.1f} m, score={score:.3f}" if nearest is not None
                else f"{category}: no POIs, score=0.000")
    return score


def get_nearby_pois(user_point: Point, pois_m: gpd.GeoDataFrame, category: str, threshold: float):
    """Return list of POIs within threshold meters of user_point."""
    nearby_pois_m = pois_m[
        (pois_m["category"] == category)
        & (pois_m["distance"] <= threshold)
    ]
    if nearby_pois_m.empty:
        return []
    
    nearby_pois = convert_to_geo_crs(nearby_pois_m)
    
    nearby_pois_list = []
    for _, row in nearby_pois.iterrows():
        nearby_pois_list.append({
            "category": category,
            "name": row.get("name") or row.get("stop_name"),
            "distance": round(float(row["distance"]), 1),
            "geometry": row["geometry"].__geo_interface__,
        })
    logger.info(f"{category}: {len(nearby_pois_list)} nearby POIs ≤ {threshold} m")
    return nearby_pois_list


def find_nearest_pois(pois_with_dist, thresholds):
    """Return nearest POI info (name + distance) for each category."""
    nearest_all = []
    for category in thresholds.keys():
        subset = pois_with_dist[pois_with_dist["category"] == category]
        if subset.empty:
            nearest_all.append({"category": category, "name": None, "distance": None})
            continue
        nearest_row = subset.loc[subset["distance"].idxmin()]
        nearest_all.append({
            "category": category,
            "name": nearest_row.get("name") or nearest_row.get("stop_name"),
            "distance": round(float(nearest_row["distance"]), 1),
        })
    return nearest_all


def analyze_walkability_at_location(lat, lon, thresholds, weights, pois):
    """Compute walkability index for a given location.
      1. Calculates category scores (linear decay).
      2. Finds nearby POIs for each category.
      3. Combines scores with weights.
      4. Returns overall index + breakdown + nearby + nearest.
    """
    logger.info(f"Analyzing walkability for lat={lat}, lon={lon}")
    user_point = Point(lon, lat)
    
    # Adds one 'distance' column (meters) to POI dataset for this user point
    pois_m = convert_to_metric_crs(pois.copy())
    user_point_m = convert_to_metric_crs(user_point)
    pois_m["distance"] = pois_m.distance(user_point_m)
    
    categories_breakdown, all_pois_nearby = [], []

    for category, threshold in thresholds.items():
        weight = float(weights.get(category, 1))
        if weight <= 0:
            continue

        score = calculate_category_score(user_point, pois_m, category, threshold)
        nearby_pois = get_nearby_pois(user_point, pois_m, category, threshold)

        categories_breakdown.append({
            "category": category,
            "score": score,
            "weight": weight,
            "threshold": threshold,
            "nearby_count": len(nearby_pois),
        })
        
        all_pois_nearby.extend(nearby_pois)

    index = combine_scores(categories_breakdown)
    nearest_pois = find_nearest_pois(pois_m, thresholds)

    result = {
        "center": {"lat": lat, "lon": lon},
        "index": index,
        "breakdown": categories_breakdown,
        "nearby_pois": all_pois_nearby,
        "nearest_pois": nearest_pois,
    }
    logger.info(f"Analysis complete: {len(all_pois_nearby)} total nearby POIs")
    return result
