import math
from agent.types import Spot, DayPlan, Itinerary

def distance(a: Spot, b: Spot) -> float:
    return math.sqrt((a.lat - b.lat)**2 + (a.lon - b.lon)**2) * 111

def plan_itinerary(city: str, spots: list[Spot], days: int) -> Itinerary:
    daily = [[] for _ in range(days)]

    # 简单 round-robin 分天
    for i, spot in enumerate(spots):
        daily[i % days].append(spot)

    day_plans = []
    for i, day_spots in enumerate(daily):
        total = 0
        for j in range(len(day_spots) - 1):
            total += distance(day_spots[j], day_spots[j + 1])

        day_plans.append(
            DayPlan(day=i+1, spots=day_spots, total_distance_km=round(total, 2))
        )

    return Itinerary(city=city, days=day_plans)
