"""Route Agent

Provides simple route estimation using haversine distances from utils.
This agent returns ordered legs with estimated travel_time_minutes and distance_km.
"""
from typing import Dict, List
from utils import haversine, travel_time_minutes_km


class RouteAgent:
    @classmethod
    def run(cls, input_data: Dict) -> Dict:
        # Accept itinerary as either a flat list or a list with 'day' keys.
        itinerary = input_data.get("itinerary") or []
        # Group by day if present
        by_day = {}
        for item in itinerary:
            day = item.get("day", 1)
            by_day.setdefault(day, []).append(item)

        legs_by_day = {}
        for day, items in sorted(by_day.items()):
            legs = []
            for i in range(len(items) - 1):
                a = items[i]
                b = items[i + 1]
                lat1, lon1 = a.get("lat"), a.get("lon")
                lat2, lon2 = b.get("lat"), b.get("lon")
                # If coords missing, skip leg
                if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
                    continue
                dist = haversine(lat1, lon1, lat2, lon2)
                minutes = travel_time_minutes_km(dist)
                legs.append({
                    "from": a.get("name", f"place_{i}"),
                    "to": b.get("name", f"place_{i+1}"),
                    "distance_km": round(dist, 2),
                    "travel_time_minutes": int(minutes),
                })
            legs_by_day[day] = legs

        return {"legs_by_day": legs_by_day}
