"""Food Agent

Provides recommended restaurants / food places for destinations.
"""
from typing import List

try:
    from data_loader import DataLoader
    _FOODS = DataLoader.load_foods() or None
except Exception:
    _FOODS = None


class FoodAgent:
    """Simple food recommendation agent backed by an internal dataset or the
    JSON dataset when available.
    """

    DATA = {
        "Goa": ["Thalassa", "Martin's Corner", "Fisherman's Wharf"],
        "Mysore": ["RRR Restaurant", "Mylari Hotel", "Gufha Restaurant"],
        "Bangalore": ["Vidyarthi Bhavan", "MTR", "Toit Brewery"],
        "Delhi": ["Karim's", "Paranthe Wali Gali", "Bukhara"],
    }

    # Support rich food dataset: keep RICH_FOODS for detailed info and
    # convert to names-only lists for DATA to preserve compatibility.
    RICH_FOODS = None
    if _FOODS:
        try:
            RICH_FOODS = {k.title(): v for k, v in _FOODS.items()}
            normalized = {}
            for city, items in RICH_FOODS.items():
                if isinstance(items, list) and items and isinstance(items[0], dict):
                    normalized[city] = [it.get("name", "") for it in items if it.get("name")]
                elif isinstance(items, list):
                    normalized[city] = items
                else:
                    normalized[city] = []
            DATA = normalized
        except Exception:
            RICH_FOODS = None

    @classmethod
    def get_recommendations(cls, destination: str, top_n: int = 5) -> List[str]:
        """Return a list of recommended food places for a destination.

        Args:
            destination: City name (case-insensitive)
            top_n: Maximum number of results
        """
        if not destination:
            return []
        key = destination.strip().title()
        if key in cls.DATA:
            return cls.DATA[key][:top_n]

        return []


if __name__ == "__main__":
    print(FoodAgent.get_recommendations("Mysore"))
