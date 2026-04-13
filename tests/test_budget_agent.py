from agents.budget_agent import BudgetAgent


def test_budget_total_consistency():
    res = BudgetAgent.estimate("Mysore", 2)
    assert res["total"] == res["hotel"] + res["food"] + res["transport"] + res["activities"]


def test_budget_days_minimum():
    # days < 1 should be treated as 1
    res = BudgetAgent.estimate("Mysore", 0)
    assert res["hotel"] > 0
