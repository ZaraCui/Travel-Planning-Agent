OUTDOOR_CATEGORIES = {
    "outdoor",
    "beach",
    "park",
    "garden",
}

INDOOR_CATEGORIES = {
    "indoor",
    "museum",
    "shopping",
    "temple",
}

def is_outdoor(spot) -> bool:
    return spot.category in OUTDOOR_CATEGORIES

def is_indoor(spot) -> bool:
    return spot.category in INDOOR_CATEGORIES
