from agent.types import Itinerary, Spot
from agent.planner import distance

MAX_DAILY_DISTANCE_KM = 6.0  
MAX_DAILY_TIME = {
    TransportMode.WALK: 240,     # 分钟
    TransportMode.TRANSIT: 300,
    TransportMode.TAXI: 360
}

def check_daily_time(itinerary: Itinerary, mode: TransportMode):
    violations = []

    for day in itinerary.days:
        total = 0
        for i in range(len(day.spots) - 1):
            total += travel_cost(day.spots[i], day.spots[i+1], mode)

        if total > MAX_DAILY_TIME[mode]:
            violations.append({
                "day": day.day,
                "time": round(total, 1),
                "limit": MAX_DAILY_TIME[mode]
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

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple

from agent.types import Itinerary, DayPlan, Spot
from agent.planner import distance


@dataclass(frozen=True)
class ScoreConfig:
    max_daily_km: float = 6.0

    # Penalty weight: how harshly we punish exceeding the daily max.
    exceed_km_penalty: float = 25.0

    # Penalize "too empty" days (e.g., only 1 spot) when total spots allow better distribution.
    one_spot_day_penalty: float = 15.0

    # If total spots >= days * min_spots_per_day, then enforce experience expectations via penalty
    min_spots_per_day: int = 2


def compute_day_distance_km(spots: List[Spot]) -> float:
    total = 0.0
    for i in range(len(spots) - 1):
        total += distance(spots[i], spots[i + 1])
    return total


def score_itinerary(itinerary: Itinerary, cfg: ScoreConfig) -> Tuple[float, List[str]]:
    """
    Lower score is better.
    Returns: (score, reasons)
    """
    reasons: List[str] = []

    # Count total spots to decide whether "1-spot day" is actually undesirable.
    total_spots = sum(len(day.spots) for day in itinerary.days)
    days = len(itinerary.days)
    expect_min = (total_spots >= days * cfg.min_spots_per_day)

    score = 0.0

    for day in itinerary.days:
        day_km = compute_day_distance_km(day.spots)
        day.total_distance_km = round(day_km, 2)

        # Base: prefer shorter routes
        score += day_km

        # Soft constraint: exceeding max daily distance adds penalty
        if day_km > cfg.max_daily_km:
            exceed = day_km - cfg.max_daily_km
            penalty = exceed * cfg.exceed_km_penalty
            score += penalty
            reasons.append(
                f"Day {day.day}: exceeded {cfg.max_daily_km:.1f}km by {exceed:.2f}km (+{penalty:.2f})"
            )

        # Experience penalty: discourage 1-spot day when we could distribute better
        if expect_min and len(day.spots) < cfg.min_spots_per_day:
            score += cfg.one_spot_day_penalty
            reasons.append(
                f"Day {day.day}: only {len(day.spots)} spot(s) (+{cfg.one_spot_day_penalty:.2f})"
            )

    return score, reasons
