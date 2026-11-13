"""Generate GeoJSON circles from config/facilities.json.

Uses only the Python standard library. Circle coordinates are approximate
geodesic points suitable for review, not a survey boundary.
"""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
config = json.loads((ROOT / "config" / "facilities.json").read_text())
radius = config["geofence"]["radius_meters"]
earth_radius = 6_378_137.0


def circle(lon, lat, radius_m, points=96):
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    angular = radius_m / earth_radius
    result = []
    for i in range(points + 1):
        bearing = 2 * math.pi * i / points
        lat2 = math.asin(
            math.sin(lat_r) * math.cos(angular)
            + math.cos(lat_r) * math.sin(angular) * math.cos(bearing)
        )
        lon2 = lon_r + math.atan2(
            math.sin(bearing) * math.sin(angular) * math.cos(lat_r),
            math.cos(angular) - math.sin(lat_r) * math.sin(lat2),
        )
        result.append([math.degrees(lon2), math.degrees(lat2)])
    return result


features = []
for facility in config["facilities"]:
    point = [facility["longitude"], facility["latitude"]]
    features.append(
        {
            "type": "Feature",
            "properties": {
                "id": facility["id"],
                "name": facility["name"],
                "address": facility["address"],
                "radius_meters": radius,
                "activation_status": config["geofence"]["activation_status"],
                "review_flags": facility["review_flags"],
            },
            "geometry": {"type": "Point", "coordinates": point},
        }
    )
    features.append(
        {
            "type": "Feature",
            "properties": {
                "id": facility["id"] + "-geofence",
                "facility_id": facility["id"],
                "name": facility["name"] + " — 500 m review circle",
                "radius_meters": radius,
                "activation_status": config["geofence"]["activation_status"],
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [circle(facility["longitude"], facility["latitude"], radius)],
            },
        }
    )

output = {
    "type": "FeatureCollection",
    "name": "south-portland-petroleum-terminal-review-geofences",
    "metadata": {
        "source": config["source"],
        "radius_meters": radius,
        "warning": "Circles are provisional and require visual approval.",
    },
    "features": features,
}

(ROOT / "geofences" / "facilities.geojson").write_text(
    json.dumps(output, indent=2) + "\n"
)
print("Wrote geofences/facilities.geojson")
