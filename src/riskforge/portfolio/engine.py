"""Portfolio engine (Phase 3).

Maps risk-factor returns to portfolio returns/P&L under a fixed-weight
linear approximation: R_p,t = sum_i w_i * R_i,t (blueprint formula).

This is a *risk-factor-return* portfolio, not a position/instrument-level
P&L engine — appropriate scope for a market-risk-model prototype, and it
is stated as such rather than implied to be more sophisticated.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def validate_weights(weights: dict[str, float], tol: float = 1e-6) -> None:
    total = sum(weights.values())
    if abs(total - 1.0) > tol:
        raise ValueError(f"Portfolio weights must sum to 1.0, got {total:.6f}")
    if any(w < -1.0 or w > 1.0 for w in weights.values()):
        raise ValueError("Weights outside [-1, 1] are unusual for this prototype; check inputs")


def portfolio_returns(returns_wide: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """R_p,t = sum_i w_i R_i,t"""
    validate_weights(weights)
    missing = set(weights) - set(returns_wide.columns)
    if missing:
        raise ValueError(f"Weights reference unknown risk factors: {missing}")
    w = pd.Series(weights)[returns_wide.columns.intersection(weights.keys())]
    aligned = returns_wide[w.index]
    port_ret = aligned.mul(w, axis=1).sum(axis=1)
    port_ret.name = "portfolio_return"
    return port_ret


def portfolio_pnl(port_returns: pd.Series, notional: float = 1_000_000.0) -> pd.Series:
    """Convert portfolio returns to a dollar (or base-currency) P&L series
    for a fixed notional. Prototype simplification: no rebalancing,
    compounding, or transaction costs.
    """
    pnl = port_returns * notional
    pnl.name = "portfolio_pnl"
    return pnl


def sample_covariance(returns_wide: pd.DataFrame) -> pd.DataFrame:
    return returns_wide.cov()


def portfolio_variance(weights: dict[str, float], cov: pd.DataFrame) -> float:
    """sigma_p^2 = w' Sigma w"""
    w = pd.Series(weights)[cov.columns]
    return float(w.values @ cov.values @ w.values)


def manual_check_example() -> dict:
    """A tiny hand-computable example used in tests to verify the engine
    against a manual calculation (blueprint Phase 3: 'verify against
    manual example').
    """
    returns = pd.DataFrame(
        {"A": [0.01, -0.02, 0.03], "B": [0.02, 0.00, -0.01]},
        index=pd.date_range("2024-01-01", periods=3),
    )
    weights = {"A": 0.6, "B": 0.4}
    # manual: t0: 0.6*0.01 + 0.4*0.02 = 0.014
    #         t1: 0.6*-0.02 + 0.4*0.00 = -0.012
    #         t2: 0.6*0.03 + 0.4*-0.01 = 0.014
    expected = pd.Series([0.014, -0.012, 0.014], index=returns.index, name="portfolio_return")
    return {"returns": returns, "weights": weights, "expected": expected}
