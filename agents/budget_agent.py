"""Budget Agent

Provides a simple budget estimate broken down into hotel, food, transport and activities.
The numbers are illustrative and meant for demo and learning purposes.
"""
from typing import Dict


class BudgetAgent:
    """Estimate travel costs using simple heuristics.

    This is not a real pricing engine. Values are rough defaults to make the demo
    useful and easy to extend.
    """

    # New simplified formula for demo purposes
    @classmethod
    def estimate(cls, destination: str, days: int) -> Dict[str, int]:
        """Estimate costs using the requested formula.

        Formula:
            hotel = 2500 * days
            food = 800 * days
            transport = 500 * days
            activities = 500 * days
            total = sum of above

        Returns a dict with keys hotel, food, transport, activities, total.
        """
        days = max(1, int(days or 1))
        hotel = 2500 * days
        food = 800 * days
        transport = 500 * days
        activities = 500 * days
        total = hotel + food + transport + activities

        return {
            "hotel": hotel,
            "food": food,
            "transport": transport,
            "activities": activities,
            "total": total,
        }

    @classmethod
    def run(cls, input_data: Dict) -> Dict:
        """Run-style API: accepts {'destination', 'days', 'itinerary'} and returns budget breakdown

        If 'itinerary' is provided, attempts to include expected_cost from itinerary
        into activities to give a more realistic total.
        """
        dest = input_data.get("destination")
        days = int(input_data.get("days") or 1)
        base = cls.estimate(dest, days)

        # If itinerary provided, sum expected_cost into activities
        itinerary = input_data.get("itinerary") or []
        extra = sum(it.get("expected_cost", 0) for it in itinerary)
        breakdown = dict(base)
        breakdown["activities"] = breakdown.get("activities", 0) + int(extra)
        breakdown["total"] = breakdown.get("hotel", 0) + breakdown.get("food", 0) + breakdown.get(
            "transport", 0) + breakdown.get("activities", 0)

        # Add a simple warning field
        budget_ok = input_data.get("budget") is None or breakdown["total"] <= int(input_data.get("budget") or 0)
        return {"breakdown": breakdown, "budget_ok": budget_ok}


if __name__ == "__main__":
    print(BudgetAgent.estimate("Mysore", 2))
