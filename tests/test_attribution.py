import pandas as pd
from riskforge.attribution import attribution


def test_volatility_contribution_sums_to_one():
    cov = pd.DataFrame(
        {"A": [0.0004, 0.0001], "B": [0.0001, 0.0009]}, index=["A", "B"]
    )
    weights = {"A": 0.6, "B": 0.4}
    df = attribution.volatility_contribution(weights, cov)
    assert abs(df["pct_of_portfolio_variance"].sum() - 1.0) < 1e-9


def test_factor_ranking_orders_by_avg_abs_contribution():
    df = pd.DataFrame({
        "scenario_id": ["S1", "S1", "S2", "S2"],
        "risk_factor": ["A", "B", "A", "B"],
        "factor_contribution": [-0.10, -0.01, -0.02, -0.01],
    })
    ranking = attribution.factor_ranking_across_scenarios(df)
    assert ranking.iloc[0]["risk_factor"] == "A"
