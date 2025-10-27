import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import geopandas as gpd
from app.scoring.point_model import analyze_walkability_at_location

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s:%(funcName)s — %(message)s",
    datefmt="%H:%M:%S"
)

# --- Initialize FastAPI ---
app = FastAPI()

# --- Serve static and template files ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- Load your dataset once ---
pois_gdf = gpd.read_file("data/processed/pois_all.geojson")

# --- Define the structure of input data coming from frontend ---
class Location(BaseModel):
    name: str
    lat: float
    lon: float
    
class WalkabilityInput(BaseModel):
    location: Location
    categories: list
    thresholds: list
    weights: list

# --- Routes ---

# 1. Show your index page
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/result", response_class=HTMLResponse)
def read_result(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})

# 2. Endpoint that runs your scoring logic
@app.post("/api/analyze")
def analyze_walkability_api(data: WalkabilityInput):
    print("received data: ", data)
    # TODO: make frontend return categories
    result = analyze_walkability_at_location(
        lat=Location.lat,
        lon=Location.lon,
        categories=data.categories, 
        thresholds=data.thresholds,
        weights=data.weights,
        pois=pois_gdf
    )
    # TODO: format result to match frontend 
    # previous working returned result
    # result = {
    #     "location": location,
    #     "center": {"lat": user_lat, "lon": user_lon},
    #     "index": index,
    #     "breakdown": breakdown,
    #     "buffers_m": list(thresholds.values()),
    #     "nearby": all_nearby,
    # }
    return result
