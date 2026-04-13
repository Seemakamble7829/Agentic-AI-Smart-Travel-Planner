"""Utility helpers: haversine distance, time helpers and small utilities."""
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional


def haversine(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lng points."""
    try:
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.asin(math.sqrt(a))
    except Exception:
        return float('inf')


def travel_time_minutes_km(distance_km, avg_kmh=30):
    """Estimate travel time (minutes) for distance_km using average speed."""
    if not distance_km or avg_kmh <= 0:
        return 15
    hours = distance_km / avg_kmh
    return int(round(hours * 60))


def time_to_str(dt: datetime):
    return dt.strftime("%I:%M %p")


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def get_coords(obj: Dict) -> Tuple[Optional[float], Optional[float]]:
    """Return (lat, lon) for an object that may use 'lat'/'lon' or 'lat'/'lng'.

    Returns (None, None) when not present or non-numeric.
    """
    if not obj:
        return None, None
    lat = obj.get("lat")
    lon = obj.get("lon") if obj.get("lon") is not None else obj.get("lng")
    try:
        lat = float(lat) if lat is not None else None
        lon = float(lon) if lon is not None else None
    except Exception:
        return None, None
    return lat, lon


def nearest_neighbor_order(points: List[Dict]) -> List[Dict]:
    """Order a list of places (each with lat/lon) using a greedy nearest-neighbour.

    If coordinates are missing for a point it's appended at the end in original order.
    """
    if not points:
        return []

    # Prepare list of (idx, lat, lon)
    indexed = []
    for i, p in enumerate(points):
        lat, lon = get_coords(p)
        if lat is None or lon is None:
            continue
        indexed.append((i, lat, lon))

    if not indexed:
        return points[:]  # nothing to order

    # Start from the first valid point
    used = set()
    order = []
    current_idx, cur_lat, cur_lon = indexed[0]
    used.add(current_idx)
    order.append(points[current_idx])

    remaining = {i: (lat, lon) for i, lat, lon in indexed if i != current_idx}

    def dist(a_lat, a_lon, b_lat, b_lon):
        return haversine(a_lat, a_lon, b_lat, b_lon)

    while remaining:
        # find nearest
        next_i = None
        next_d = float("inf")
        for i, (lat, lon) in remaining.items():
            d = dist(cur_lat, cur_lon, lat, lon)
            if d < next_d:
                next_d = d
                next_i = i
        if next_i is None:
            break
        order.append(points[next_i])
        cur_lat, cur_lon = remaining[next_i]
        del remaining[next_i]

    # Append any points that lacked coords or were skipped in original order
    for i, p in enumerate(points):
        if p not in order:
            order.append(p)

    return order
