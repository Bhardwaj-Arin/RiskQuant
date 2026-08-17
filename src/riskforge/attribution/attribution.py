"""Risk attribution (Phase 8): which risk factors drive portfolio risk,
under the volatility model and under specific stress scenarios.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def volatility_contribution(weights: dict[str, float], cov: pd.DataFrame) -> pd.DataFrame:
    """Component contribution to portfolio variance:
    contribution_i = w_i * (Sigma w)_i / sigma_p^2, summing to 1.0.
    Standard Euler decomposition of portfolio variance.
    """
    factors = list(weights.keys())
    w = pd.Series(weights)[factors]
    sigma_w = cov.loc[factors, factors].values @ w.values
    port_var = float(w.values @ sigma_w)
    if port_var <= 0:
        raise ValueError("Non-positive portfolio variance; check inputs")
    contrib = w.values * sigma_w / port_var
    df = pd.DataFrame({
        "risk_factor": factors,
        "weight": w.values,
        "marginal_contribution": sigma_w,
        "pct_of_portfolio_variance": contrib,
    }).sort_values("pct_of_portfolio_variance", ascending=False).reset_index(drop=True)
    return df


def scenario_contribution(scenario_result_df: pd.DataFrame) -> pd.DataFrame:
    """Rank risk factors by their loss contribution within a single
    scenario run (expects the long-format output of
    stress.scenarios.run_scenario_set for one scenario_id)."""
    ranked = scenario_result_df.copy()
    ranked["abs_contribution"] = ranked["factor_contribution"].abs()
    ranked = ranked.sort_values("abs_contribution", ascending=False)
    total = ranked["factor_contribution"].sum()
    ranked["pct_of_scenario_loss"] = ranked["factor_contribution"] / total if total != 0 else 0.0
    return ranked[["scenario_id", "risk_factor", "shock", "factor_contribution", "pct_of_scenario_loss"]]


def factor_ranking_across_scenarios(all_scenarios_df: pd.DataFrame) -> pd.DataFrame:
    """Average absolute contribution per risk factor across all scenarios
    in a stress-test set, to see which factors are consistently the
    biggest drivers."""
    g = all_scenarios_df.copy()
    g["abs_contribution"] = g["factor_contribution"].abs()
    ranking = (
        g.groupby("risk_factor")["abs_contribution"]
        .mean()
        .sort_values(ascending=False)
        .rename("avg_abs_contribution")
        .reset_index()
    )
    return ranking
