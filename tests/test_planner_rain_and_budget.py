from agents.planner_agent import PlannerAgent


def make_place(name, lat=None, lon=None, tags=None, cost=0, desc=None):
    d = {"name": name, "description": desc or f"{name} desc", "cost_estimate": cost}
    if lat is not None:
        d["lat"] = lat
    if lon is not None:
        d["lon"] = lon
    if tags is not None:
        d["tags"] = tags
    return d


def test_rainy_prefers_indoor():
    # Create two places: one outdoor (beach), one indoor (museum)
    outdoor = make_place("Sunny Beach", lat=10.0, lon=77.0, desc="Beautiful beach and promenade")
    indoor = make_place("City Museum", lat=10.01, lon=77.01, desc="Indoor exhibits and galleries")
    attractions = [outdoor, indoor]
    input_data = {
        "destination": "TestCity",
        "interests": ["beach", "culture"],
        "budget": 10000,
        "attractions": attractions,
        "foods": [],
        "weather": {"condition": "Rainy"},
        "days": 1,
    }
    out = PlannerAgent.run(input_data)
    # reasoning should mention rainy behavior
    assert any("rain" in r.lower() for r in out.get("reasoning", []))
    # ensure indoor option appears before outdoor in itinerary when rainy
    names = [i.get("name") for i in out["itinerary"]]
    assert "City Museum" in names
    assert names.index("City Museum") < names.index("Sunny Beach")


def test_budget_trimming_removes_items():
    # Create expensive attractions that force trimming
    a1 = make_place("Expensive Palace", lat=12.0, lon=77.0, cost=5000)
    a2 = make_place("Luxury Garden", lat=12.01, lon=77.01, cost=4000)
    a3 = make_place("Cheap Temple", lat=12.02, lon=77.02, cost=100)
    attractions = [a1, a2, a3]
    input_data = {
        "destination": "TestCity",
        "interests": [],
        "budget": 2000,  # very small budget
        "attractions": attractions,
        "foods": [],
        "weather": {"condition": "Sunny"},
        "days": 2,
    }
    out = PlannerAgent.run(input_data)
    # total_estimated should be <= budget after trimming
    assert out["total_estimated"] <= 2000
    # reasoning should include removal information
    assert any("removed" in r.lower() or "trimm" in r.lower() for r in out.get("reasoning", []))
