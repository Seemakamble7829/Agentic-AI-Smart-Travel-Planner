from agents.destination_agent import DestinationAgent


def test_known_city_attractions():
    attractions = DestinationAgent.get_attractions("Mysore")
    assert isinstance(attractions, list)
    assert "Mysore Palace" in attractions


def test_unknown_city_returns_empty():
    assert DestinationAgent.get_attractions("Atlantis") == []
