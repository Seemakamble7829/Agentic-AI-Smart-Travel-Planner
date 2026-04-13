"""Weather Agent

Tries to fetch real weather using OpenWeatherMap if API key present in environment.
Otherwise simulates a friendly weather response.
"""
import os
import random
from typing import Dict

import requests

from dotenv import load_dotenv


load_dotenv()


class WeatherAgent:
    """Agent to provide simple weather information for a city.

    If OPENWEATHER_API_KEY is present in environment, it will try to fetch live
    data. Otherwise it will return a simulated weather report.
    """

    @staticmethod
    def _simulate_weather() -> Dict[str, str]:
        conditions = ["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Windy"]
        temp = random.randint(18, 33)
        return {"temperature_c": f"{temp}", "condition": random.choice(conditions)}

    @classmethod
    def get_weather(cls, destination: str) -> Dict[str, str]:
        """Return weather information for a destination.

        Returns a dict with 'temperature_c' and 'condition'.
        """
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if api_key and destination:
            try:
                url = (
                    "http://api.openweathermap.org/data/2.5/weather"
                    f"?q={destination}&units=metric&appid={api_key}"
                )
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                temp = data.get("main", {}).get("temp")
                cond = data.get("weather", [{}])[0].get("description", "Unknown")
                if temp is not None:
                    return {"temperature_c": f"{int(round(temp))}", "condition": cond.title()}
            except Exception:
                # If any error occurs, fallback to simulated weather
                return cls._simulate_weather()

        # No API key -> simulate
        return cls._simulate_weather()

    @classmethod
    def run(cls, input_data: Dict) -> Dict:
        """Run-style API wrapper. Accepts {'destination'} and returns weather dict."""
        dest = input_data.get("destination")
        return cls.get_weather(dest)


if __name__ == "__main__":
    print(WeatherAgent.get_weather("Mysore"))
