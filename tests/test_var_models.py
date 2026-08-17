import numpy as np
import pandas as pd
import pytest
from scipy import stats

from riskforge.models import historical_var, parametric_var, ewma, expected_shortfall


def test_parametric_var_sign_convention_known_normal_case():
    # returns ~ N(0, 0.01^2); 99% VaR should be close to 2.326 * 0.01 (positive loss)
    rng = np.random.default_rng(0)
    returns = pd.Series(rng.normal(0, 0.01, size=5000))
    var = parametric_var.parametric_var(returns, confidence=0.99)
    expected = -stats.norm.ppf(0.01) * 0.01  # ~0.02326
    assert var > 0
    assert abs(var - expected) < 0.002


def test_parametric_var_from_moments_matches_direct_formula():
    v1 = parametric_var.parametric_var_from_moments(0.0, 0.02, confidence=0.99)
    v2 = -(0.0 + stats.norm.ppf(0.01) * 0.02)
    assert abs(v1 - v2) < 1e-12


def test_historical_var_is_positive_for_typical_return_series():
    rng = np.random.default_rng(1)
    returns = pd.Series(rng.standard_t(df=5, size=1000) * 0.01)
    var = historical_var.historical_var(returns, confidence=0.99)
    assert var > 0


def test_historical_var_matches_manual_small_example():
    # 10 returns, 90% confidence -> 10th percentile is the worst value
    returns = pd.Series([0.01, -0.05, 0.02, -0.01, 0.00, 0.03, -0.02, 0.01, -0.03, 0.015])
    var = historical_var.historical_var(returns, confidence=0.90)
    assert var > 0
    assert var >= 0.03  # worst return is -0.05; 10th pct should be near there


def test_es_at_least_as_large_as_var_historical():
    rng = np.random.default_rng(2)
    returns = pd.Series(rng.standard_t(df=4, size=2000) * 0.015)
    var = historical_var.historical_var(returns, confidence=0.99)
    es = expected_shortfall.historical_es(returns, confidence=0.99)
    assert es >= var - 1e-9  # ES (average tail loss) should not be below the VaR threshold


def test_parametric_es_greater_than_parametric_var_normal():
    rng = np.random.default_rng(3)
    returns = pd.Series(rng.normal(0.0005, 0.012, size=3000))
    var = parametric_var.parametric_var(returns, confidence=0.99)
    es = expected_shortfall.parametric_es(returns, confidence=0.99)
    assert es > var


def test_rolling_historical_var_no_lookahead_length():
    rng = np.random.default_rng(4)
    returns = pd.Series(rng.normal(0, 0.01, size=600),
                         index=pd.bdate_range("2020-01-01", periods=600))
    window = 250
    series = historical_var.rolling_historical_var(returns, 0.99, window)
    assert len(series) == len(returns) - window
    assert series.index[0] == returns.index[window]


def test_ewma_volatility_reacts_to_shock():
    # constant tiny returns, then one big shock -> vol should jump after the shock
    returns = pd.Series([0.001] * 60 + [0.15] + [0.001] * 20)
    vol = ewma.ewma_volatility(returns, lam=0.94, seed_window=30)
    assert vol.iloc[61] > vol.iloc[59]  # jump right after the shock
