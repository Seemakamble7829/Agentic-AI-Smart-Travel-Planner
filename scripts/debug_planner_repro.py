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


a1 = make_place("Expensive Palace", lat=12.0, lon=77.0, cost=5000)
a2 = make_place("Luxury Garden", lat=12.01, lon=77.01, cost=4000)
a3 = make_place("Cheap Temple", lat=12.02, lon=77.02, cost=100)
input_data = {
    "destination": "TestCity",
    "interests": [],
    "budget": 2000,
    "attractions": [a1,a2,a3],
    "foods": [],
    "weather": {"condition":"Sunny"},
    "days": 2,
}
out = PlannerAgent.run(input_data)
print('total_estimated=', out['total_estimated'])
print('itinerary:')
for it in out['itinerary']:
    print(it['name'], it['expected_cost'], 'day', it['day'], 'slot', it['slot'])
print('reasoning:')
for r in out['reasoning']:
    print('-', r)
