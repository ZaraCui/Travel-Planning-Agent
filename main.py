import json
import folium

from agent.types import Spot
from agent.planner import plan_itinerary_soft_constraints
from agent.constraints import ScoreConfig

# Load data
spots = [
    Spot(**s)
    for s in json.load(open("data/spots_tokyo.json", encoding="utf-8"))
]

# Configure soft constraints
cfg = ScoreConfig(
    max_daily_km=6.0,
    exceed_km_penalty=25.0,
    one_spot_day_penalty=15.0,
    min_spots_per_day=2
)

# Run agent planner (search + scoring)
itinerary, score, reasons = plan_itinerary_soft_constraints(
    city="Tokyo",
    spots=spots,
    days=3,
    cfg=cfg,
    trials=200
)

# Print self-check report
print(f"Best score: {score:.2f}")

if reasons:
    print("Self-check report:")
    for r in reasons:
        print(" -", r)
else:
    print("Self-check report: no penalties")

# Visualize on map
m = folium.Map(location=[spots[0].lat, spots[0].lon], zoom_start=12)
colors = ["red", "blue", "green"]

for i, day in enumerate(itinerary.days):
    coords = []
    for s in day.spots:
        folium.Marker(
            [s.lat, s.lon],
            popup=f"Day {day.day}: {s.name}"
        ).add_to(m)
        coords.append([s.lat, s.lon])

    if len(coords) >= 2:
        folium.PolyLine(coords, color=colors[i % len(colors)]).add_to(m)

m.save("output/map.html")
print("Saved output/map.html")
