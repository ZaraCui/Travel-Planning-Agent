import math
from agent.types import Spot, DayPlan, Itinerary

def distance(a: Spot, b: Spot) -> float:
    return math.sqrt((a.lat - b.lat)**2 + (a.lon - b.lon)**2) * 111

def plan_itinerary(city: str, spots: list[Spot], days: int) -> Itinerary:
    # 1️⃣ 先整体排序（粗略：按经度）
    spots_sorted = sorted(spots, key=lambda s: (s.lon, s.lat))

    # 2️⃣ 切成 days 份
    chunk_size = max(1, len(spots_sorted) // days)
    chunks = [
        spots_sorted[i:i + chunk_size]
        for i in range(0, len(spots_sorted), chunk_size)
    ]

    chunks = chunks[:days]  # 防止多出来

    day_plans = []
    for i, chunk in enumerate(chunks):
        ordered = nearest_neighbor_path(chunk)

        total = 0.0
        for j in range(len(ordered) - 1):
            total += distance(ordered[j], ordered[j + 1])

        day_plans.append(
            DayPlan(
                day=i + 1,
                spots=ordered,
                total_distance_km=round(total, 2)
            )
        )

    return Itinerary(city=city, days=day_plans)


def nearest_neighbor_path(spots: list[Spot]) -> list[Spot]:
    if not spots:
        return []

    unvisited = spots[:]
    path = [unvisited.pop(0)]

    while unvisited:
        last = path[-1]
        next_spot = min(
            unvisited,
            key=lambda s: distance(last, s)
        )
        path.append(next_spot)
        unvisited.remove(next_spot)

    return path
