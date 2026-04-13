import pytest

from agents.planner_agent import PlannerAgent


def make_place(name, lat=None, lon=None, tags=None, cost=0):
    d = {"name": name, "description": f"{name} desc", "cost_estimate": cost}
    if lat is not None:
        d["lat"] = lat
    if lon is not None:
        d["lon"] = lon
    if tags is not None:
        d["tags"] = tags
    return d


def test_multi_day_itinerary_basic():
    # 4 attractions, 2 days -> expect 4 slots assigned (no food)
    attractions = [make_place(f"P{i}", lat=12.0 + i * 0.01, lon=77.0 + i * 0.01) for i in range(4)]
    input_data = {
        "destination": "TestCity",
        "interests": ["food"],
        "budget": 10000,
        "attractions": attractions,
        "foods": [],
        "weather": {},
        "days": 2,
    }

    out = PlannerAgent.run(input_data)
    assert "itinerary" in out
    itin = out["itinerary"]
    # should include all attractions (4)
    assert len([i for i in itin if i.get("slot") != "Evening Meal"]) == 4
    # days must be within 1..2
    assert all(1 <= i.get("day", 1) <= 2 for i in itin)


def test_budget_flag():
    # small budget cause budget_ok False
    attractions = [make_place("Single", lat=12.0, lon=77.0, cost=1000)]
    input_data = {
        "destination": "TestCity",
        "interests": [],
        "budget": 10,
        "attractions": attractions,
        "foods": [],
        "weather": {},
        "days": 1,
    }
    out = PlannerAgent.run(input_data)
    assert out["budget_ok"] is False
