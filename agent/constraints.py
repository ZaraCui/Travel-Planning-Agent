from agent.types import Itinerary, Spot
from agent.planner import distance

MAX_DAILY_DISTANCE_KM = 6.0  # 你可以先设小一点方便观察效果

def check_daily_distance(itinerary: Itinerary):
    violations = []

    for day in itinerary.days:
        total = 0.0
        for i in range(len(day.spots) - 1):
            total += distance(day.spots[i], day.spots[i + 1])

        day.total_distance_km = round(total, 2)

        if total > MAX_DAILY_DISTANCE_KM:
            violations.append({
                "day": day.day,
                "distance": round(total, 2),
                "limit": MAX_DAILY_DISTANCE_KM
            })

    return violations

def repair_itinerary(itinerary: Itinerary):
    violations = check_daily_distance(itinerary)

    if not violations:
        return itinerary

    for v in violations:
        day_idx = v["day"] - 1
        day = itinerary.days[day_idx]

        # 只有一个点就没法拆
        if len(day.spots) <= 1:
            continue

        # 找到“最远的 spot”（最后一个，先简单处理）
        moved_spot = day.spots.pop()

        # 找一个最近的其他天
        target_day = None
        min_dist = float("inf")

        for other in itinerary.days:
            if other.day == day.day:
                continue
            if not other.spots:
                continue

            d = distance(moved_spot, other.spots[-1])
            if d < min_dist:
                min_dist = d
                target_day = other

        if target_day:
            target_day.spots.append(moved_spot)

    return itinerary
