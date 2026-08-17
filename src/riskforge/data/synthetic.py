"""Synthetic risk-factor data generator.

Purpose
-------
This sandbox has no internet access, so RiskForge-QRM ships a synthetic
data generator that produces *statistically realistic* multi-asset price
series (fat tails, volatility clustering via a simple GARCH-like process,
and cross-asset correlation) for development, testing and demonstration.

IMPORTANT: this is clearly labelled synthetic data. For a real submission,
swap in `loader.load_from_yfinance(...)` or `loader.load_from_csv(...)`,
both provided in this package, when running with internet access.
Never present synthetic-data results as real market results.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_FACTORS = ["EQUITY_INDEX", "RATES_10Y", "FX_USD", "OIL", "GOLD"]

# Rough annualized vol assumptions per factor (illustrative, not calibrated
# to any specific real index) and a plausible correlation structure.
_ANNUAL_VOL = {
    "EQUITY_INDEX": 0.18,
    "RATES_10Y": 0.012,   # yield-change vol, not a return vol
    "FX_USD": 0.09,
    "OIL": 0.32,
    "GOLD": 0.14,
}

_CORR = pd.DataFrame(
    [
        [1.00, -0.30, 0.10, 0.35, -0.20],
        [-0.30, 1.00, -0.10, -0.05, 0.10],
        [0.10, -0.10, 1.00, 0.15, -0.15],
        [0.35, -0.05, 0.15, 1.00, -0.05],
        [-0.20, 0.10, -0.15, -0.05, 1.00],
    ],
    index=DEFAULT_FACTORS,
    columns=DEFAULT_FACTORS,
)


def _garch_like_vol(n: int, base_vol_daily: float, rng: np.random.Generator,
                     persistence: float = 0.90, shock_weight: float = 0.08) -> np.ndarray:
    """Simple GARCH(1,1)-flavoured volatility path so returns exhibit
    volatility clustering rather than i.i.d. constant-vol noise.
    """
    long_run_var = base_vol_daily ** 2
    var = np.empty(n)
    var[0] = long_run_var
    innovations = rng.standard_t(df=6, size=n)  # fat tails
    innovations /= innovations.std()
    returns = np.empty(n)
    for t in range(n):
        if t > 0:
            var[t] = (
                (1 - persistence - shock_weight) * long_run_var
                + persistence * var[t - 1]
                + shock_weight * returns[t - 1] ** 2
            )
        returns[t] = np.sqrt(max(var[t], 1e-10)) * innovations[t]
    return returns


def generate_risk_factor_returns(
    start_date: str,
    end_date: str,
    factors: list[str] | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate correlated, fat-tailed, volatility-clustered daily returns
    for the given risk factors.

    Returns
    -------
    DataFrame indexed by business-day date, one column per risk factor,
    containing simple returns (or, for RATES_10Y, an absolute yield change
    treated as the 'return' for that factor throughout this project).
    """
    factors = factors or DEFAULT_FACTORS
    dates = pd.bdate_range(start=start_date, end=end_date)
    n = len(dates)
    rng = np.random.default_rng(seed)

    # Independent GARCH-like series per factor
    raw = np.column_stack(
        [_garch_like_vol(n, _ANNUAL_VOL[f] / np.sqrt(252), rng) for f in factors]
    )
    # Standardize then impose target correlation via Cholesky, preserving
    # each factor's own marginal (already fat-tailed, clustered) shape.
    z = (raw - raw.mean(axis=0)) / raw.std(axis=0)
    corr = _CORR.loc[factors, factors].values
    L = np.linalg.cholesky(corr)
    correlated = z @ L.T
    scaled = correlated * raw.std(axis=0, keepdims=True) + raw.mean(axis=0, keepdims=True)

    df = pd.DataFrame(scaled, index=dates, columns=factors)
    df.index.name = "date"
    return df


def returns_to_price_levels(returns: pd.DataFrame, start_level: float = 100.0) -> pd.DataFrame:
    """Convert simple returns to a price/level series (base = start_level).
    RATES_10Y is treated as a level series built by cumulative sum of yield
    changes instead of compounding, since it is a rate, not a price.
    """
    levels = pd.DataFrame(index=returns.index, columns=returns.columns, dtype=float)
    for col in returns.columns:
        if col == "RATES_10Y":
            levels[col] = start_level / 100.0 * 2.5 + returns[col].cumsum()  # start ~2.5%
        else:
            levels[col] = start_level * (1 + returns[col]).cumprod()
    return levels


def generate_market_prices(
    start_date: str, end_date: str, factors: list[str] | None = None, seed: int = 42
) -> pd.DataFrame:
    """Convenience wrapper: returns a long-format market_prices-style table
    matching the sql/schema.sql market_prices table.
    """
    factors = factors or DEFAULT_FACTORS
    rets = generate_risk_factor_returns(start_date, end_date, factors, seed)
    levels = returns_to_price_levels(rets)
    long = levels.reset_index().melt(id_vars="date", var_name="risk_factor", value_name="value")
    long["source"] = "synthetic"
    long["retrieved_at"] = pd.Timestamp.utcnow()
    return long.sort_values(["risk_factor", "date"]).reset_index(drop=True)
