from agents.food_agent import FoodAgent


def test_known_city_foods():
    foods = FoodAgent.get_recommendations("Mysore")
    assert isinstance(foods, list)
    assert "RRR Restaurant" in foods


def test_unknown_city_foods_empty():
    assert FoodAgent.get_recommendations("UnknownCity") == []
