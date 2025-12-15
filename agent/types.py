from pydantic import BaseModel
from typing import List

class Spot(BaseModel):
    name: str
    lat: float
    lon: float
    category: str  # indoor / outdoor / food / museum

class DayPlan(BaseModel):
    day: int
    spots: List[Spot]
    total_distance_km: float = 0.0

class Itinerary(BaseModel):
    city: str
    days: List[DayPlan]
