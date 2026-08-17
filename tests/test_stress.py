import pandas as pd
import pytest
from riskforge.stress import scenarios


WEIGHTS = {"EQUITY_INDEX": 0.5, "RATES_10Y": 0.2, "FX_USD": 0.15, "OIL": 0.1, "GOLD": 0.05}


def test_apply_scenario_matches_manual_calculation():
    shocks = {"EQUITY_INDEX": -0.20, "OIL": -0.30}
    result = scenarios.apply_scenario(WEIGHTS, shocks)
    expected_return = 0.5 * -0.20 + 0.1 * -0.30
    assert abs(result["portfolio_return"] - expected_return) < 1e-12
    assert abs(result["portfolio_loss"] - (-expected_return)) < 1e-12


def test_apply_scenario_rejects_unknown_factor():
    with pytest.raises(ValueError):
        scenarios.apply_scenario(WEIGHTS, {"UNKNOWN_FACTOR": -0.1})


def test_run_scenario_set_produces_expected_rows():
    scenario_list = [
        {"id": "S1", "description": "test", "shocks": {"EQUITY_INDEX": -0.1, "OIL": -0.2}},
    ]
    df = scenarios.run_scenario_set(WEIGHTS, scenario_list)
    assert len(df) == 2  # one row per shocked factor
    assert set(df["risk_factor"]) == {"EQUITY_INDEX", "OIL"}


def test_sensitivity_analysis_is_linear_in_shock():
    df = scenarios.sensitivity_analysis(WEIGHTS, "EQUITY_INDEX", [-0.2, -0.1, 0.0, 0.1])
    # portfolio_loss should scale linearly with shock given fixed weight
    losses = df.set_index("shock")["portfolio_loss"]
    slope = (losses.loc[-0.1] - losses.loc[0.0]) / (-0.1 - 0.0)
    assert abs(slope - (-WEIGHTS["EQUITY_INDEX"])) < 1e-9
