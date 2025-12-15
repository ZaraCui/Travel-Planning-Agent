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

def travel_cost(a: Spot, b: Spot, mode: TransportMode) -> float:
    """
    返回“代价”，单位统一为分钟（更通用）
    """
    base_km = distance(a, b)

    if mode == TransportMode.WALK:
        speed_kmh = 4.5
        return (base_km / speed_kmh) * 60

    if mode == TransportMode.TRANSIT:
        # 粗略模型：更快但有等待
        speed_kmh = 20
        wait_time = 5
        return (base_km / speed_kmh) * 60 + wait_time

    if mode == TransportMode.TAXI:
        speed_kmh = 30
        return (base_km / speed_kmh) * 60

from __future__ import annotations
import random
from copy import deepcopy
from typing import List, Tuple

from agent.types import Spot, DayPlan, Itinerary
from agent.constraints import ScoreConfig, score_itinerary


def nearest_neighbor_path(spots: List[Spot]) -> List[Spot]:
    if not spots:
        return []
    unvisited = spots[:]
    path = [unvisited.pop(0)]
    while unvisited:
        last = path[-1]
        nxt = min(unvisited, key=lambda s: distance(last, s))
        path.append(nxt)
        unvisited.remove(nxt)
    return path


def build_initial_itinerary(city: str, spots: List[Spot], days: int) -> Itinerary:
    # Simple spatial sort; later you can use clustering.
    spots_sorted = sorted(spots, key=lambda s: (s.lon, s.lat))

    # Split into days as evenly as possible (balanced chunk sizes)
    chunks: List[List[Spot]] = [[] for _ in range(days)]
    for i, s in enumerate(spots_sorted):
        chunks[i % days].append(s)

    day_plans: List[DayPlan] = []
    for i in range(days):
        ordered = nearest_neighbor_path(chunks[i])
        day_plans.append(DayPlan(day=i + 1, spots=ordered, total_distance_km=0.0))

    return Itinerary(city=city, days=day_plans)


def try_move_one_spot(itin: Itinerary) -> Itinerary:
    """
    Move one spot from one day to another (random), then re-order both affected days.
    """
    new_itin = deepcopy(itin)
    days = new_itin.days

    from_candidates = [d for d in days if len(d.spots) >= 2]
    if not from_candidates:
        return new_itin

    src = random.choice(from_candidates)
    dst = random.choice([d for d in days if d.day != src.day])

    # Choose a spot to move (avoid always popping last; random gives exploration)
    idx = random.randrange(len(src.spots))
    moved = src.spots.pop(idx)
    dst.spots.append(moved)

    # Re-order affected days
    src.spots = nearest_neighbor_path(src.spots)
    dst.spots = nearest_neighbor_path(dst.spots)

    return new_itin


def try_swap_spots_between_days(itin: Itinerary) -> Itinerary:
    """
    Swap one spot between two days, then re-order both.
    """
    new_itin = deepcopy(itin)
    days = new_itin.days
    if len(days) < 2:
        return new_itin

    d1, d2 = random.sample(days, 2)
    if not d1.spots or not d2.spots:
        return new_itin

    i = random.randrange(len(d1.spots))
    j = random.randrange(len(d2.spots))

    d1.spots[i], d2.spots[j] = d2.spots[j], d1.spots[i]

    d1.spots = nearest_neighbor_path(d1.spots)
    d2.spots = nearest_neighbor_path(d2.spots)

    return new_itin


def plan_itinerary_soft_constraints(
    city: str,
    spots: List[Spot],
    days: int,
    cfg: ScoreConfig,
    trials: int = 200
) -> Tuple[Itinerary, float, List[str]]:
    """
    Generate many candidate itineraries via local edits, score them, and pick best.
    Returns: (best_itinerary, best_score, best_reasons)
    """
    random.seed(0)  # determinism for debugging

    base = build_initial_itinerary(city, spots, days)
    best = base
    best_score, best_reasons = score_itinerary(best, cfg)

    # Explore neighborhood
    current = base
    for _ in range(trials):
        # Randomly choose an edit operator
        if random.random() < 0.6:
            candidate = try_move_one_spot(current)
        else:
            candidate = try_swap_spots_between_days(current)

        candidate_score, candidate_reasons = score_itinerary(candidate, cfg)

        # Accept if better; simple hill-climbing
        if candidate_score < best_score:
            best = candidate
            best_score = candidate_score
            best_reasons = candidate_reasons
            current = candidate  # continue exploring from improved state

    return best, best_score, best_reasons
