"""Data-quality checks (Phase 2 of the project blueprint).

Checks: missing values, duplicates, date alignment, outliers, stale
values. Produces a structured quality report rather than silently
"fixing" data, so problems stay visible.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class DataQualityReport:
    n_rows: int
    n_risk_factors: int
    duplicates: pd.DataFrame
    missing_values: pd.DataFrame
    date_gaps: dict[str, list[pd.Timestamp]]
    stale_runs: pd.DataFrame
    outlier_returns: pd.DataFrame
    passed: bool = field(init=False)

    def __post_init__(self):
        self.passed = (
            self.duplicates.empty
            and self.missing_values.empty
            and all(len(v) == 0 for v in self.date_gaps.values())
        )

    def summary(self) -> str:
        lines = [
            "RiskForge-QRM Data Quality Report",
            "=" * 40,
            f"Rows: {self.n_rows}, Risk factors: {self.n_risk_factors}",
            f"Duplicates: {len(self.duplicates)}",
            f"Missing values: {len(self.missing_values)}",
            f"Risk factors with date gaps: {sum(1 for v in self.date_gaps.values() if v)}",
            f"Stale (repeated-value) runs flagged: {len(self.stale_runs)}",
            f"Outlier returns (|r| > 20%): {len(self.outlier_returns)}",
            f"Overall PASS: {self.passed}",
        ]
        return "\n".join(lines)


def check_duplicates(prices_long: pd.DataFrame) -> pd.DataFrame:
    dup_mask = prices_long.duplicated(subset=["date", "risk_factor"], keep=False)
    return prices_long[dup_mask].sort_values(["risk_factor", "date"])


def check_missing_values(prices_long: pd.DataFrame) -> pd.DataFrame:
    return prices_long[prices_long["value"].isna() | (prices_long["value"] <= 0)]


def check_date_gaps(prices_long: pd.DataFrame) -> dict[str, list[pd.Timestamp]]:
    """Flag business-day gaps > 1 day within each factor's own date range
    (holidays cause small legitimate gaps; this flags larger anomalies)."""
    gaps: dict[str, list[pd.Timestamp]] = {}
    for factor, g in prices_long.groupby("risk_factor"):
        dates = pd.DatetimeIndex(sorted(g["date"].unique()))
        expected = pd.bdate_range(dates.min(), dates.max())
        missing = expected.difference(dates)
        # Only flag runs of 4+ consecutive missing business days as anomalies
        # (1-3 day gaps are routine holidays).
        flagged = []
        if len(missing) > 0:
            missing_sorted = sorted(missing)
            run = [missing_sorted[0]]
            for d in missing_sorted[1:]:
                if (d - run[-1]).days <= 3:
                    run.append(d)
                else:
                    if len(run) >= 4:
                        flagged.extend(run)
                    run = [d]
            if len(run) >= 4:
                flagged.extend(run)
        gaps[factor] = flagged
    return gaps


def check_stale_values(prices_long: pd.DataFrame, min_run: int = 5) -> pd.DataFrame:
    """Flag runs of `min_run`+ consecutive identical values per factor."""
    flagged_rows = []
    for factor, g in prices_long.sort_values("date").groupby("risk_factor"):
        vals = g["value"].values
        run_len = 1
        for i in range(1, len(vals)):
            if vals[i] == vals[i - 1]:
                run_len += 1
            else:
                run_len = 1
            if run_len >= min_run:
                flagged_rows.append(g.iloc[i])
    if not flagged_rows:
        return pd.DataFrame(columns=prices_long.columns)
    return pd.DataFrame(flagged_rows)


def check_outlier_returns(returns_wide: pd.DataFrame, threshold: float = 0.20) -> pd.DataFrame:
    mask = returns_wide.abs() > threshold
    # Call .stack() with no dropna arg (pandas >=3.0 forbids passing it, and
    # its new implementation already excludes NA rows), then defensively
    # dropna() again so this is correct across older pandas versions too.
    stacked = returns_wide.where(mask).stack().dropna()
    return stacked.rename("value").reset_index()


def run_quality_checks(prices_long: pd.DataFrame, returns_wide: pd.DataFrame) -> DataQualityReport:
    return DataQualityReport(
        n_rows=len(prices_long),
        n_risk_factors=prices_long["risk_factor"].nunique(),
        duplicates=check_duplicates(prices_long),
        missing_values=check_missing_values(prices_long),
        date_gaps=check_date_gaps(prices_long),
        stale_runs=check_stale_values(prices_long),
        outlier_returns=check_outlier_returns(returns_wide),
    )


def long_to_wide_levels(prices_long: pd.DataFrame) -> pd.DataFrame:
    wide = prices_long.pivot(index="date", columns="risk_factor", values="value").sort_index()
    return wide


def levels_to_returns(levels_wide: pd.DataFrame, rate_factors: tuple[str, ...] = ("RATES_10Y",)) -> pd.DataFrame:
    """Simple returns for price-like factors; absolute change for rate
    factors (a rate 'return' is a level change, not a percentage return)."""
    returns = pd.DataFrame(index=levels_wide.index[1:], columns=levels_wide.columns, dtype=float)
    for col in levels_wide.columns:
        if col in rate_factors:
            returns[col] = levels_wide[col].diff().iloc[1:]
        else:
            returns[col] = levels_wide[col].pct_change().iloc[1:]
    return returns
