"""Expected Shortfall (Phase 4).

Historical ES_alpha = -mean(R | R <= q_(1-alpha)): average tail loss
beyond the VaR threshold, more informative about tail severity than VaR
alone.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def historical_es(returns: pd.Series, confidence: float = 0.99) -> float:
    q = returns.quantile(1 - confidence)
    tail = returns[returns <= q]
    if tail.empty:
        # Degenerate case (extremely small sample); fall back to the quantile
        return float(-q)
    return float(-tail.mean())


def parametric_es(returns: pd.Series, confidence: float = 0.99) -> float:
    """Closed-form ES under a normal assumption:
    ES_alpha = mu_loss + sigma * phi(z) / (1 - confidence)
    expressed here directly as a positive loss number.
    """
    mu = returns.mean()
    sigma = returns.std(ddof=1)
    z = stats.norm.ppf(1 - confidence)
    es = -mu + sigma * stats.norm.pdf(z) / (1 - confidence)
    return float(es)


def rolling_historical_es(returns: pd.Series, confidence: float = 0.99, window: int = 250) -> pd.Series:
    if len(returns) <= window:
        raise ValueError(f"Need more than {window} observations, got {len(returns)}")
    forecasts = {}
    for t in range(window, len(returns)):
        window_data = returns.iloc[t - window:t]
        forecasts[returns.index[t]] = historical_es(window_data, confidence)
    result = pd.Series(forecasts, name="historical_es")
    result.index.name = "date"
    return result
