"""Backtesting harness (Phase 5).

Builds the per-forecast-date table: forecast_date, model_name, VaR,
realized P&L, realized loss, exception_flag, where an exception is
realized_loss > VaR under a positive-loss convention.
"""
from __future__ import annotations

import pandas as pd


def build_backtest_table(var_forecasts: pd.Series, realized_returns: pd.Series,
                          model_name: str) -> pd.DataFrame:
    """`var_forecasts` and `realized_returns` must be aligned so that the
    VaR forecast at date t is compared against the realized return that
    actually occurred on date t (the return the forecast was *for*).
    """
    aligned = pd.DataFrame({
        "var": var_forecasts,
        "realized_return": realized_returns.reindex(var_forecasts.index),
    }).dropna()
    aligned["realized_loss"] = -aligned["realized_return"]
    aligned["exception_flag"] = aligned["realized_loss"] > aligned["var"]
    aligned["model_id"] = model_name
    aligned.index.name = "forecast_date"
    return aligned.reset_index()


def exception_rate(backtest_table: pd.DataFrame) -> float:
    if backtest_table.empty:
        raise ValueError("Empty backtest table")
    return float(backtest_table["exception_flag"].mean())


def compare_models(backtest_tables: dict[str, pd.DataFrame], confidence: float) -> pd.DataFrame:
    """Summary table across models: exception rate vs the target
    (1 - confidence), average exceedance size, etc."""
    target_rate = 1 - confidence
    rows = []
    for name, table in backtest_tables.items():
        exc = table[table["exception_flag"]]
        rows.append({
            "model_id": name,
            "n_forecasts": len(table),
            "n_exceptions": int(table["exception_flag"].sum()),
            "exception_rate": exception_rate(table),
            "target_rate": target_rate,
            "avg_exceedance_size": float((exc["realized_loss"] - exc["var"]).mean()) if not exc.empty else 0.0,
            "avg_var": float(table["var"].mean()),
        })
    return pd.DataFrame(rows).set_index("model_id")
