"""Itinerary Agent

Combines attractions, food recommendations and weather to build a
day-by-day itinerary.
"""
from typing import List, Dict


class ItineraryAgent:
    """Generates a simple structured itinerary.

    The algorithm is intentionally simple: distribute attractions across days
    and insert meal/food recommendations. This is easy to read and to extend.
    """

    @staticmethod
    def _chunk_list(items: List[str], n: int) -> List[List[str]]:
        """Split items into n roughly equal chunks (for days)."""
        if n <= 0:
            return [items]
        chunks = [[] for _ in range(n)]
        for i, item in enumerate(items):
            chunks[i % n].append(item)
        return chunks

    @classmethod
    def generate(
        cls,
        destination: str,
        days: int,
        interests: str,
        attractions: List[str],
        food_places: List[str],
        weather: Dict[str, str],
    ) -> List[str]:
        """Create a day-by-day plan as a list of strings.

        Args:
            destination: City name
            days: Number of days
            interests: User interests (free text)
            attractions: List of attractions to include
            food_places: List of food places
            weather: Weather dict for notes

        Returns:
            List of day descriptions.
        """
        days = max(1, days)
        chunks = cls._chunk_list(attractions, days)
        itinerary = []
        for day_idx in range(days):
            day_num = day_idx + 1
            parts = [f"Day {day_num}"]
            # Attractions for the day
            todays_attractions = chunks[day_idx] if day_idx < len(chunks) else []
            if todays_attractions:
                for a in todays_attractions:
                    parts.append(f"Visit {a}")
            else:
                parts.append("Free time / explore the city")

            # Meal suggestion
            if food_places:
                meal = food_places[day_idx % len(food_places)]
                parts.append(f"Lunch at {meal}")

            # Add interest-driven suggestion
            if interests:
                parts.append(f"Suggested activity: explore {interests.strip()}")

            # Weather note
            if weather:
                parts.append(f"Weather: {weather.get('condition', '')} {weather.get('temperature_c', '')}°C")

            itinerary.append("\n".join(parts))

        return itinerary


if __name__ == "__main__":
    print(ItineraryAgent.generate("Mysore", 2, "history food", ["Mysore Palace", "Chamundi Hills"], ["RRR Restaurant"], {"condition":"Cloudy","temperature_c":"24"}))
