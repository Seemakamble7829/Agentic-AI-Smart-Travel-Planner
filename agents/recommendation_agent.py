"""Recommendation Agent

Provides attractions and food recommendations using the project's JSON
datasets (via DataLoader). Returns rich objects (dicts) when available.
"""
from typing import Dict
from data_loader import DataLoader


class RecommendationAgent:
    """Return {'attractions': [...], 'foods': [...]}"""

    @classmethod
    def run(cls, input_data: Dict) -> Dict:
        dest = (input_data.get("destination") or "").title()
        dests = DataLoader.load_destinations() or {}
        foods = DataLoader.load_foods() or {}
        attractions = dests.get(dest, [])
        food_list = foods.get(dest, [])

        # Deduplicate foods by name and limit to useful number
        seen = set()
        unique_foods = []
        for f in food_list:
            name = f.get("name") if isinstance(f, dict) else str(f)
            if name in seen:
                continue
            seen.add(name)
            unique_foods.append(f)

        # Return more than one restaurant when available
        return {"attractions": attractions or [], "foods": unique_foods}
