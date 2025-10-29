# walkability

to run the app:
uvicorn app.main:app --reload
uvicorn app.main:app --reload --log-level debug
from cmd


It returns a Python dictionary (which FastAPI automatically converts to JSON) with five top-level keys:

Key	Type	Description	Example
"location"	str	Human-readable location name (passed from frontend).	"Downtown Montreal"
"center"	dict	The geographic coordinates of the user location.	{"lat": 45.5017, "lon": -73.5673}
"index"	float	The combined walkability score (0–100).	78.4
"breakdown"	list[dict]	Per-category breakdown with distances, weights, and nearest POIs.	(see below)
"buffers_m"	list[float]	List of all distance thresholds (used to draw circles).	[500, 800, 1000]
"nearby"	list[dict]	GeoJSON-like objects representing nearby POIs per category.	(see below)
🧮 Example of the full JSON returned to the frontend
{
  "location": "Downtown Montreal",
  "center": {"lat": 45.5017, "lon": -73.5673},
  "index": 78.4,
  "breakdown": [
    {
      "name": "parks",
      "score": 0.92,
      "weight": 0.3,
      add buffer
      "nearest_dist": 210.5,
      "nearest_name": "Mount Royal Park",
      "nearby_count": 3
    },
    {
      "name": "metro",
      "score": 0.76,
      "weight": 0.4,
      "nearest_dist": 620.0,
      "nearest_name": "Peel Station",
      "nearby_count": 1
    },
    {
      "name": "grocery",
      "score": 0.67,
      "weight": 0.3,
      "nearest_dist": 480.0,
      "nearest_name": "Metro Plus",
      "nearby_count": 2
    }
  ],
  "buffers_m": [1000, 800, 600], 
  "nearby": [
    {
      "category": "parks",
      "name": "Mount Royal Park",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.5878, 45.5043]
      }
    },
    {
      "category": "parks",
      "name": "Cabot Square",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.5792, 45.4954]
      }
    },
    {
      "category": "metro",
      "name": "Peel Station",
      "geometry": {
        "type": "Point",
        "coordinates": [-73.5739, 45.4999]
      }
    }
  ]
}