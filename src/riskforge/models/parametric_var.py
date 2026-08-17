"""Parametric (variance-covariance) VaR (Phase 4).

VaR_alpha = -(mu + z_(1-alpha) * sigma), where z_(1-alpha) is the
*negative* lower-tail normal quantile. Sign convention is easy to get
wrong -- see tests/test_var_models.py for an explicit worked check.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def parametric_var(returns: pd.Series, confidence: float = 0.99) -> float:
    mu = returns.mean()
    sigma = returns.std(ddof=1)
    z = stats.norm.ppf(1 - confidence)  # negative number, e.g. -2.326 for 99%
    var = -(mu + z * sigma)
    return float(var)


def parametric_var_from_moments(mu: float, sigma: float, confidence: float = 0.99) -> float:
    z = stats.norm.ppf(1 - confidence)
    return float(-(mu + z * sigma))


def rolling_parametric_var(
    returns: pd.Series, confidence: float = 0.99, window: int = 250
) -> pd.Series:
    if len(returns) <= window:
        raise ValueError(f"Need more than {window} observations, got {len(returns)}")
    forecasts = {}
    for t in range(window, len(returns)):
        window_data = returns.iloc[t - window:t]
        forecasts[returns.index[t]] = parametric_var(window_data, confidence)
    result = pd.Series(forecasts, name="parametric_var")
    result.index.name = "date"
    return result
