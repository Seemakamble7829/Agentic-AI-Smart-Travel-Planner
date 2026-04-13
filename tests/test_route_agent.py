from agents.route_agent import RouteAgent


def make_point(name, lat, lon, day=1):
    return {"name": name, "lat": lat, "lon": lon, "day": day}


def test_route_legs_by_day():
    itin = [
        make_point("A", 12.0, 77.0, day=1),
        make_point("B", 12.01, 77.01, day=1),
        make_point("C", 13.0, 78.0, day=2),
        make_point("D", 13.02, 78.02, day=2),
    ]

    out = RouteAgent.run({"itinerary": itin})
    assert "legs_by_day" in out
    legs_by_day = out["legs_by_day"]
    # day 1 should have one leg (A->B), day2 one leg (C->D)
    assert 1 in legs_by_day and 2 in legs_by_day
    assert len(legs_by_day[1]) == 1
    assert len(legs_by_day[2]) == 1
    leg = legs_by_day[1][0]
    assert "distance_km" in leg and "travel_time_minutes" in leg
