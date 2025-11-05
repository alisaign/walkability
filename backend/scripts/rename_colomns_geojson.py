import geopandas as gpd

path = "data/processed/quartierreferencehabitation.geojson"

gdf = gpd.read_file(path)

if "nom_qr" in gdf.columns:
    gdf = gdf.rename(columns={"nom_qr": "NOM"})
    gdf.to_file(path, driver="GeoJSON", encoding="utf-8")
    print("Column renamed and file updated successfully.")
else:
    print("Column 'nom_qr' not found in file.")
