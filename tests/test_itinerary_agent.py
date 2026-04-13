from agents.itinerary_agent import ItineraryAgent


def test_itinerary_length_and_content():
    attractions = ["A1", "A2", "A3"]
    foods = ["F1", "F2"]
    weather = {"condition": "Sunny", "temperature_c": "30"}
    it = ItineraryAgent.generate("TestCity", 2, "sightseeing", attractions, foods, weather)
    assert isinstance(it, list)
    assert len(it) == 2
    assert any("Day 1" in d for d in it)
    assert any("Lunch at" in d for d in it)
