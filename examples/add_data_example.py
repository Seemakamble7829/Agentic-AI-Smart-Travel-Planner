"""Example script showing how to use DataLoader to add cities, places and food entries.

Run from the project root (where `data_loader.py` lives):

    python examples/add_data_example.py

This script is intended as a quick example for editing the JSON dataset now that the in-app admin UI
was removed. The `DataLoader` functions will create or update files in the `data/` folder.
"""
from data_loader import DataLoader


def main():
    city = "SampleCity"
    print(f"Adding city: {city}")
    ok = DataLoader.add_city(city)
    print("add_city result:", ok)

    place = {
        "name": "Sample Museum",
        "lat": 12.9716,
        "lng": 77.5946,
        "description": "A small interactive museum about local history."
    }
    print(f"Adding place to {city}: {place['name']}")
    ok = DataLoader.add_place(city, place)
    print("add_place result:", ok)

    food = {
        "name": "Sample Eats",
        "cuisine": "Fusion",
        "rating": 4.3,
        "description": "Casual spot with local twists on classics."
    }
    print(f"Adding food to {city}: {food['name']}")
    ok = DataLoader.add_food(city, food)
    print("add_food result:", ok)

    print("Current destinations for", city, ":")
    dests = DataLoader.load_destinations()
    print(dests.get(city))


if __name__ == "__main__":
    main()
