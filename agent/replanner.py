from agent.planner import nearest_neighbor_path
from agent.types import Itinerary
from agent.semantics import is_indoor,is_outdoor

def replan_single_day(itinerary, day_idx):
    day = itinerary.days[day_idx]

    outdoor_spots = [s for s in day.spots if is_outdoor(s)]
    if not outdoor_spots:
        return False  # nothing to fix

    # Other day's indoor spot
    for other_day in itinerary.days:
        if other_day.day == day.day:
            continue

        indoor_candidates = [s for s in other_day.spots if is_indoor(s)]
        if indoor_candidates:
            # swap
            day.spots.remove(outdoor_spots[0])
            other_day.spots.remove(indoor_candidates[0])

            day.spots.append(indoor_candidates[0])
            other_day.spots.append(outdoor_spots[0])
            return True

    return False
