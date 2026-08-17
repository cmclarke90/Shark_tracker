#!/usr/bin/env python3
"""
Fetches the OCEARCH shark tracker feed (served via Mapotic), filters to
sharks, computes distance from a home location, and writes the nearest
few to a small JSON file. Runs on a GitHub Actions schedule - the
PyPortal can't reach the source feed directly (Mapotic/Cloudflare serves
an ECDSA certificate the ESP32 co-processor's TLS stack can't handle),
so this fetches it from a normal internet connection instead and the
PyPortal reads the small result from raw.githubusercontent.com.
"""

import json
import math
import urllib.request

HOME_LAT = 33.767840
HOME_LON = -78.775733

SHARKS_URL = "https://www.mapotic.com/api/v1/maps/3413/pois.geojson/?h=20"
OUTPUT_PATH = "sharks_nearest.json"
NEAREST_SHARK_COUNT = 5


def haversine_miles(lat1, lon1, lat2, lon2):
    radius = 3958.8
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def short_species(species):
    # "White Shark (Carcharodon carcharias)" -> "White Shark"
    if not species:
        return "Shark"
    paren = species.find(" (")
    return species[:paren] if paren != -1 else species


def main():
    request = urllib.request.Request(
        SHARKS_URL, headers={"User-Agent": "pyportal-shark-relay/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    nearest = []
    for feature in data["features"]:
        props = feature.get("properties", {})

        if props.get("category_name", {}).get("en") != "Sharks":
            continue

        coords = feature.get("geometry", {}).get("coordinates")
        if not coords or len(coords) < 2:
            continue

        lon, lat = coords[0], coords[1]
        distance = haversine_miles(HOME_LAT, HOME_LON, lat, lon)

        nearest.append({
            "name": (props.get("name") or "Unknown")[:14],
            "species": short_species(props.get("species")),
            "distance": round(distance, 1),
            "last_move": props.get("last_move_datetime") or "",
        })

    nearest.sort(key=lambda item: item["distance"])
    nearest = nearest[:NEAREST_SHARK_COUNT]

    with open(OUTPUT_PATH, "w") as f:
        json.dump(nearest, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(nearest)} nearest sharks to {OUTPUT_PATH}")
    for entry in nearest:
        print(f" - {entry['name']} | {entry['species']} | {entry['distance']} mi")


if __name__ == "__main__":
    main()
