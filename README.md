# Walkability Index Web Application

## 1. Environment Setup
**Python version:** 3.10+

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or
source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

**requirements.txt**
```
fastapi
uvicorn
geopandas
shapely
jinja2
```

---

## 2. Directory Structure
```
app/
├── main.py
├── scoring/
│   ├── point_model.py
│   ├── area_model.py
│   ├── utils.py
│   └── __init__.py
├── static/
│   └── map.js
└── templates/
    ├── index.html
    └── result.html
data/
└── processed/pois_all.geojson
```

---

## 3. Running the Application
Start FastAPI backend:
```bash
uvicorn app.main:app --reload
uvicorn main:app --reload

```

Default address: `http://127.0.0.1:8000/`

Routes:
- `/` – main page
- `/result` – result page
- `/api/analyze` – POST endpoint for walkability computation

---

## 4. API Specification
### Endpoint
`POST /api/analyze`

### Input (JSON)
```json
{
  "lat": 45.5017,
  "lon": -73.5673,
  "categories": ["metro","bus","grocery","restaurants","parks","schools","healthcare"],
  "thresholds": [200,1000,500,300,400,800,1000],
  "weights": [3,2,3,2,2,2,2]
}
```

### Output (JSON)
```json
{
  "location": "Verdun",
  "center": {"lat": 45.474, "lon": -73.58},
  "index": 81.2,
  "breakdown": [
    {
      "name": "parks",
      "score": 0.92,
      "weight": 0.4,
      "buffer": 800,
      "nearest_dist": 210.5,
      "nearest_name": "Arthur-Therrien Park",
      "nearby_count": 3
    }
  ],
  "buffers_m": [800,600],
  "nearby": [
    {
      "category": "parks",
      "name": "Arthur-Therrien Park",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.58, 45.48]
      }
    }
  ],
  "neighborhood": "Verdun",
  "gradient_layer": { "type": "FeatureCollection", "features": [...] }
}
```

---

## 5. Data Requirements
**File:** `data/processed/pois_all.geojson`

**Fields required:**
- `geometry` (Point)
- `category` (string)
- optional: `name`, `stop_name`

**CRS:**
- Input/Output: EPSG:4326 (WGS84)
- Processing: EPSG:32188 (NAD83 / MTM zone 8)

---

## 6. Core Functions
| File | Function | Description |
|------|-----------|-------------|
| `point_model.py` | `analyze_walkability_at_location()` | Compute walkability index for a single point |
|  | `calculate_category_score()` | Compute 0–1 score for a category |
|  | `get_nearby_pois()` | Return nearby POIs within threshold |
| `area_model.py` | `analyze_walkability_by_neighborhood()` | Build gradient map layer for neighborhood |
|  | `combine_category_layers()` | Weighted overlay of category layers |
| `utils.py` | `convert_to_metric_crs()` / `convert_to_geo_crs()` | CRS conversion |
|  | `linear_decay()` | Linear distance–score function |
|  | `get_neighborhood_for_location()` | Find neighborhood polygon by coordinate |

---

## 7. CRS and Distance
| Purpose | CRS | Units |
|----------|-----|-------|
| Input/Output | EPSG:4326 | degrees |
| Internal Processing | EPSG:32188 | meters |

All calculations use metric CRS (EPSG:32188) for distances in meters.

---

## 8. Logging and Debugging
Start with debug level:
```bash
uvicorn app.main:app --reload --log-level debug
```

Exception handlers in `main.py`:
- `debug_exception_handler` → prints runtime tracebacks
- `validation_exception_handler` → prints validation errors and raw JSON body

---

## 9. Frontend Integration
- `index.html`: form for user input; builds JSON payload; sends to `/api/analyze`
- `result.html`: renders response and visualizations
- `map.js`: initializes Leaflet maps  
  - `initWalkabilityMap()` → nearby POIs and buffers  
  - `initNeighborhoodGradientMap()` → gradient map layer

---

## 10. Execution Flow
1. User submits form in `index.html`.
2. JavaScript builds JSON payload and sends POST to `/api/analyze`.
3. FastAPI validates payload against `WalkabilityInput` model.
4. Backend runs:
   - `analyze_walkability_at_location()`
   - `get_neighborhood_for_location()`
   - `analyze_walkability_by_neighborhood()`
5. Combined results returned as JSON.
6. `result.html` renders breakdown and maps using Leaflet.

---

## 11. Dataset and Neighborhood Notes
- POI dataset must cover Montréal region.
- Each feature must include a valid `category`.
- Missing categories return score = 0.
- Neighborhood polygons must use EPSG:4326 CRS.

---

## 12. Test Request
```bash
curl -X POST "http://127.0.0.1:8000/api/analyze" -H "Content-Type: application/json" -d "{"lat":45.5017,"lon":-73.5673,"categories":["parks"],"thresholds":[500],"weights":[3]}"
```

---

## 13. Deployment
- Backend serves API and HTML templates.
- Static assets mounted at `/static`.
- Default port: 8000 (open or forward if deploying remotely).
- Dataset paths are relative to project root.
- No database required; uses GeoJSON file.

---

## 14. Technical Notes
- Developed with Python 3.11 on Windows.
- EPSG:32188 used for metric projection (Montréal).
- Dataset loaded once on startup.
- Output formatted in GeoJSON for map compatibility.
- Single FastAPI process is sufficient for local and small-scale use.
