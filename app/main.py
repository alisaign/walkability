from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import geopandas as gpd
from app.scoring import analyze_walkability

# --- Initialize FastAPI ---
app = FastAPI()

# --- Serve static and template files ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- Load your dataset once ---
pois_gdf = gpd.read_file("data/processed/pois_all.geojson")

# --- Define the structure of input data coming from frontend ---
class WalkabilityInput(BaseModel):
    location: str
    lat: float
    lon: float
    thresholds: dict
    weights: dict

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
    result = analyze_walkability(
        location=data.location,
        user_lat=data.lat,
        user_lon=data.lon,
        thresholds=data.thresholds,
        weights=data.weights,
        gdf=pois_gdf
    )
    return result
