import pytest
from riskforge.portfolio import engine


def test_manual_check_example_matches_hand_calculation():
    check = engine.manual_check_example()
    result = engine.portfolio_returns(check["returns"], check["weights"])
    assert (result.round(6) == check["expected"].round(6)).all()


def test_validate_weights_rejects_non_unit_sum():
    with pytest.raises(ValueError):
        engine.validate_weights({"A": 0.5, "B": 0.3})


def test_validate_weights_accepts_unit_sum():
    engine.validate_weights({"A": 0.6, "B": 0.4})  # should not raise


def test_portfolio_returns_rejects_unknown_factor():
    check = engine.manual_check_example()
    with pytest.raises(ValueError):
        engine.portfolio_returns(check["returns"], {"A": 0.5, "C": 0.5})


def test_portfolio_variance_matches_manual_two_asset_formula():
    import pandas as pd
    cov = pd.DataFrame({"A": [0.0004, 0.0001], "B": [0.0001, 0.0009]}, index=["A", "B"])
    weights = {"A": 0.6, "B": 0.4}
    var = engine.portfolio_variance(weights, cov)
    expected = 0.6**2 * 0.0004 + 0.4**2 * 0.0009 + 2 * 0.6 * 0.4 * 0.0001
    assert abs(var - expected) < 1e-12
