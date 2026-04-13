"""Destination Agent

Provides top attractions for supported destinations using an internal dataset.
"""
from typing import List

try:
    # Try to use dataset loader if available
    from data_loader import DataLoader
    _LOADED = DataLoader.load_destinations() or None
except Exception:
    _LOADED = None


class DestinationAgent:
    """Simple destination agent that returns attractions from a built-in dataset
    or from the JSON dataset if present.
    """

    # Built-in fallback dataset
    DATA = {
        "Goa": [
            "Calangute Beach",
            "Baga Beach",
            "Fort Aguada",
            "Basilica of Bom Jesus",
            "Dudhsagar Waterfalls",
        ],
        "Mysore": [
            "Mysore Palace",
            "Chamundi Hills",
            "Brindavan Gardens",
            "St. Philomena's Church",
            "Mysore Zoo",
        ],
        "Bangalore": [
            "Lalbagh Botanical Garden",
            "Bangalore Palace",
            "Cubbon Park",
            "Vidhana Soudha",
            "Commercial Street",
        ],
        "Delhi": [
            "Red Fort",
            "Qutub Minar",
            "India Gate",
            "Humayun's Tomb",
            "Lotus Temple",
        ],
    }

    # If loader provided dataset, prefer it but keep compatibility.
    # The JSON dataset may contain rich objects (dicts). We store the raw
    # rich dataset in RICH_DATA and populate DATA with names-only lists so
    # existing consumers (UI/tests) continue to receive List[str].
    RICH_DATA = None
    if _LOADED:
        try:
            RICH_DATA = {k.title(): v for k, v in _LOADED.items()}
            # Convert rich objects to names-only for DATA
            normalized = {}
            for city, items in RICH_DATA.items():
                if isinstance(items, list) and items and isinstance(items[0], dict):
                    normalized[city] = [it.get("name", "") for it in items if it.get("name")]
                elif isinstance(items, list):
                    normalized[city] = items
                else:
                    normalized[city] = []
            DATA = normalized
        except Exception:
            # Fall back to built-in DATA if something goes wrong
            RICH_DATA = None

    @classmethod
    def get_attractions(cls, destination: str, top_n: int = 5) -> List[str]:
        """Return a list of top attractions for a destination.

        It first tries the dataset, and falls back to a partial match or empty list.
        """
        if not destination:
            return []

        key = destination.strip().title()
        if key in cls.DATA:
            return cls.DATA[key][:top_n]

        # Partial match fallback
        for city, attractions in cls.DATA.items():
            if key.lower() in city.lower():
                return attractions[:top_n]

        return []


if __name__ == "__main__":
    print(DestinationAgent.get_attractions("Mysore", 3))
