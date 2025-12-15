import json
import folium
from agent.types import Spot
from agent.planner import plan_itinerary

spots = [Spot(**s) for s in json.load(open("data/spots_tokyo.json"))]

itinerary = plan_itinerary("Tokyo", spots, days=3)

m = folium.Map(location=[spots[0].lat, spots[0].lon], zoom_start=12)

colors = ["red", "blue", "green"]

for i, day in enumerate(itinerary.days):
    coords = []
    for s in day.spots:
        folium.Marker([s.lat, s.lon], popup=f"Day {day.day}: {s.name}").add_to(m)
        coords.append([s.lat, s.lon])
    folium.PolyLine(coords, color=colors[i]).add_to(m)

m.save("output/map.html")
print("Saved output/map.html")

from agent.constraints import check_daily_distance, repair_itinerary

violations = check_daily_distance(itinerary)

if violations:
    print("Violations detected:", violations)
    itinerary = repair_itinerary(itinerary)

transport_mode = TransportMode.WALK  # 用户选择
