from agents.destination_agent import DestinationAgent
from agents.food_agent import FoodAgent
from agents.weather_agent import WeatherAgent
from agents.budget_agent import BudgetAgent
from agents.itinerary_agent import ItineraryAgent
from data_loader import DataLoader


def build_plan(destination, days=2, budget=5000, interests="history food"):
    attractions = DestinationAgent.get_attractions(destination)
    foods = FoodAgent.get_recommendations(destination)
    weather = WeatherAgent.get_weather(destination)
    budget_est = BudgetAgent.estimate(destination, days)
    itinerary = ItineraryAgent.generate(destination, days, interests, attractions, foods, weather)
    rich_places = DataLoader.load_destinations().get(destination.title(), [])
    rich_foods = DataLoader.load_foods().get(destination.title(), [])

    print("\n" + "="*40)
    print(f"Travel plan for: {destination} ({days} days)")
    print("="*40)
    print("\nWeather:")
    print(f"  {weather.get('condition')} {weather.get('temperature_c')}°C")

    print("\nTop Attractions (rich data if available):")
    if rich_places:
        for p in rich_places:
            if isinstance(p, dict):
                print(f"  - {p.get('name')} - {p.get('description')} (lat={p.get('lat')}, lng={p.get('lng')})")
            else:
                print(f"  - {p}")
    else:
        for p in attractions:
            print(f"  - {p}")

    print("\nFood Recommendations (rich data if available):")
    if rich_foods:
        for f in rich_foods:
            if isinstance(f, dict):
                print(f"  - {f.get('name')} | cuisine={f.get('cuisine')} | rating={f.get('rating')} | {f.get('description','')}")
            else:
                print(f"  - {f}")
    else:
        for f in foods:
            print(f"  - {f}")

    print("\nItinerary:")
    for day in itinerary:
        print(day)

    print("\nEstimated Budget:")
    for k, v in budget_est.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    build_plan('Mysore', days=2)
    build_plan('Goa', days=3)
