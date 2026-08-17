"""Historical VaR (Phase 4).

Uses the empirical distribution of a rolling window of past portfolio
returns -- fewer distributional assumptions than the parametric model.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def historical_var(returns: pd.Series, confidence: float = 0.99) -> float:
    """VaR_alpha = -Q_(1-alpha)(R), reported as a positive loss number."""
    if returns.empty:
        raise ValueError("Empty returns series")
    q = returns.quantile(1 - confidence)
    return float(-q)


def rolling_historical_var(
    returns: pd.Series, confidence: float = 0.99, window: int = 250
) -> pd.Series:
    """Rolling out-of-sample forecast: VaR at t uses only returns up to
    and including t-1 (strictly backward-looking, no look-ahead bias).
    """
    if len(returns) <= window:
        raise ValueError(f"Need more than {window} observations, got {len(returns)}")
    var_forecasts = {}
    for t in range(window, len(returns)):
        window_data = returns.iloc[t - window:t]  # strictly before date t
        var_forecasts[returns.index[t]] = historical_var(window_data, confidence)
    result = pd.Series(var_forecasts, name="historical_var")
    result.index.name = "date"
    return result
