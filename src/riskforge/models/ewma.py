"""EWMA volatility and EWMA-based VaR (Phase 4).

sigma_t^2 = lambda * sigma_(t-1)^2 + (1 - lambda) * r_(t-1)^2

RiskMetrics-style decay (default lambda = 0.94 for daily data), then the
estimated conditional sigma feeds a parametric VaR calculation so recent
volatility regimes matter more than a flat rolling window.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def ewma_volatility(returns: pd.Series, lam: float = 0.94, seed_window: int = 30) -> pd.Series:
    """Recursive EWMA variance -> volatility series, seeded with the
    simple variance of the first `seed_window` observations."""
    r = returns.values
    n = len(r)
    if n <= seed_window:
        raise ValueError(f"Need more than {seed_window} observations, got {n}")
    var = np.empty(n)
    var[:seed_window] = np.var(r[:seed_window], ddof=1)
    for t in range(seed_window, n):
        var[t] = lam * var[t - 1] + (1 - lam) * r[t - 1] ** 2
    vol = pd.Series(np.sqrt(var), index=returns.index, name="ewma_volatility")
    return vol


def ewma_var(returns: pd.Series, confidence: float = 0.99, lam: float = 0.94,
             seed_window: int = 30, mu_mode: str = "rolling_mean",
             mean_window: int = 250) -> pd.Series:
    """EWMA-volatility-based parametric VaR forecast series.

    mu_mode:
      - "zero": assume zero mean (common short-horizon VaR simplification)
      - "rolling_mean": use a trailing rolling mean of returns
    """
    vol = ewma_volatility(returns, lam=lam, seed_window=seed_window)
    z = stats.norm.ppf(1 - confidence)
    if mu_mode == "zero":
        mu = pd.Series(0.0, index=returns.index)
    elif mu_mode == "rolling_mean":
        mu = returns.rolling(mean_window, min_periods=seed_window).mean().fillna(0.0)
    else:
        raise ValueError("mu_mode must be 'zero' or 'rolling_mean'")
    var_series = -(mu + z * vol)
    var_series.name = "ewma_var"
    return var_series


def rolling_ewma_var_forecast(
    returns: pd.Series, confidence: float = 0.99, lam: float = 0.94,
    window: int = 250,
) -> pd.Series:
    """Out-of-sample forecast: at each t, VaR uses EWMA vol estimated from
    data strictly before t (recomputed each step to avoid look-ahead)."""
    if len(returns) <= window:
        raise ValueError(f"Need more than {window} observations, got {len(returns)}")
    forecasts = {}
    z = stats.norm.ppf(1 - confidence)
    for t in range(window, len(returns)):
        hist = returns.iloc[:t]  # strictly before date t
        vol = ewma_volatility(hist, lam=lam, seed_window=min(30, len(hist) - 1))
        sigma_t = vol.iloc[-1]
        mu_t = hist.iloc[-window:].mean()
        forecasts[returns.index[t]] = float(-(mu_t + z * sigma_t))
    result = pd.Series(forecasts, name="ewma_var")
    result.index.name = "date"
    return result
