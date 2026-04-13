import os
from agents.weather_agent import WeatherAgent


def test_weather_simulation_when_no_api_key(monkeypatch):
    # Ensure environment has no OPENWEATHER_API_KEY
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    w = WeatherAgent.get_weather("Mysore")
    assert isinstance(w, dict)
    assert "temperature_c" in w and "condition" in w


def test_weather_response_format(monkeypatch):
    # Even if API key is present but API fails, agent should return proper keys
    monkeypatch.setenv("OPENWEATHER_API_KEY", "invalid_key_for_test")
    w = WeatherAgent.get_weather("Mysore")
    assert isinstance(w, dict)
    assert "temperature_c" in w and "condition" in w
