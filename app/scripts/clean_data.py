from app.scripts.convert_to_geojson import convert_to_geojson
import geopandas as gpd
from pathlib import Path

def prepare_transit_data():
    """Convert shapefile, clean, and save processed GeoJSON."""
    # 1️⃣ Convert shapefile → GeoJSON (already returns the output path)
    geojson_path = convert_to_geojson("data/raw/stm_sig/stm_arrets_sig.shp", "metro_bus")

    # 2️⃣ Load into GeoDataFrame
    gdf = gpd.read_file(geojson_path)

    # 3️⃣ Keep only useful fields
    keep = ["stop_id", "stop_name", "route_id", "wheelchair", "geometry"]
    gdf = gdf[keep]

    # 4️⃣ Drop duplicates
    gdf = gdf.drop_duplicates(subset=["stop_id"])

    # 5️⃣ Normalize text fields
    gdf["stop_name"] = gdf["stop_name"].astype(str).str.strip()
    gdf["route_id"] = gdf["route_id"].astype(str).str.strip()

    # 6️⃣ Add category for later use
    gdf["category"] = "transit"

    # 7️⃣ Save cleaned version
    out_dir = Path("data/processed")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "metro_bus_clean.geojson"
    gdf.to_file(out_path, driver="GeoJSON")

    print(f"✅ Cleaned dataset saved to {out_path}")
    return out_path

prepare_transit_data()