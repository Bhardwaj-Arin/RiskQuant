"""Stress testing (Phase 6): historical, hypothetical, sensitivity and
multi-factor scenarios applied through the same linear risk-factor ->
portfolio-return mapping used elsewhere in the project.
"""
from __future__ import annotations

import pandas as pd


def apply_scenario(weights: dict[str, float], shocks: dict[str, float]) -> dict:
    """Apply a shock vector to portfolio weights under the linear mapping
    R_p = sum_i w_i * shock_i. Returns portfolio loss and per-factor
    contribution.
    """
    missing = set(shocks) - set(weights)
    if missing:
        raise ValueError(f"Shock references risk factors not in portfolio: {missing}")
    contributions = {f: weights[f] * shocks[f] for f in shocks}
    portfolio_return = sum(contributions.values())
    return {
        "portfolio_return": portfolio_return,
        "portfolio_loss": -portfolio_return,
        "factor_contributions": contributions,
    }


def run_scenario_set(weights: dict[str, float], scenarios: list[dict]) -> pd.DataFrame:
    """`scenarios` is a list of {"id": ..., "description": ..., "shocks": {...}}
    as loaded from configs/stress_scenarios.yaml."""
    rows = []
    for sc in scenarios:
        result = apply_scenario(weights, sc["shocks"])
        for factor, shock in sc["shocks"].items():
            rows.append({
                "scenario_id": sc["id"],
                "description": sc.get("description", ""),
                "risk_factor": factor,
                "shock": shock,
                "factor_contribution": result["factor_contributions"][factor],
                "portfolio_loss": result["portfolio_loss"],
            })
    return pd.DataFrame(rows)


def sensitivity_analysis(weights: dict[str, float], factor: str,
                          shock_range: list[float]) -> pd.DataFrame:
    """One-factor-at-a-time sensitivity: vary a single risk factor over a
    range of shocks, holding all others at zero."""
    rows = []
    for shock in shock_range:
        result = apply_scenario(weights, {factor: shock})
        rows.append({"risk_factor": factor, "shock": shock,
                      "portfolio_loss": result["portfolio_loss"]})
    return pd.DataFrame(rows)


def historical_worst_day_scenario(returns_wide: pd.DataFrame, weights: dict[str, float]) -> dict:
    """Historical stress: replay the single worst observed portfolio-return
    day in the sample, with its date and shock vector documented (per
    blueprint: 'do not label the worst day a crisis without documenting
    date and reason')."""
    from riskforge.portfolio.engine import portfolio_returns
    port_ret = portfolio_returns(returns_wide, weights)
    worst_date = port_ret.idxmin()
    shocks = returns_wide.loc[worst_date].to_dict()
    result = apply_scenario(weights, shocks)
    return {
        "date": worst_date,
        "shocks": shocks,
        "portfolio_loss": result["portfolio_loss"],
        "note": "Worst observed day in the sample dataset used for this "
                "prototype run; document the specific date and reason "
                "before presenting this as a 'crisis scenario'.",
    }
