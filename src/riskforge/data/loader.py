"""Data loading: synthetic (default, offline), yfinance (real data, needs
internet), or local CSV (e.g. a UBS-style data extract).

Data principle (blueprint): store raw data separately from processed data,
never overwrite raw files, record source and retrieval date.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

from . import synthetic

RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def load_from_synthetic(start_date: str, end_date: str, factors: list[str] | None = None,
                         seed: int = 42) -> pd.DataFrame:
    """Offline, reproducible synthetic dataset. Used by default in this
    sandbox and by the test suite. Clearly tagged source='synthetic'.
    """
    return synthetic.generate_market_prices(start_date, end_date, factors, seed)


def load_from_yfinance(tickers: dict[str, str], start_date: str, end_date: str) -> pd.DataFrame:
    """Load real data via yfinance. Requires internet access and the
    `yfinance` package (both available on your local machine, not in this
    sandbox). `tickers` maps risk_factor name -> yfinance ticker symbol,
    e.g. {"EQUITY_INDEX": "^GSPC", "OIL": "CL=F", "GOLD": "GC=F"}.
    """
    try:
        import yfinance as yf
    except ImportError as e:
        raise ImportError(
            "yfinance is not installed. Run: pip install yfinance"
        ) from e

    frames = []
    for factor, ticker in tickers.items():
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if data.empty:
            raise ValueError(f"No data returned for {ticker} ({factor})")
        s = data["Close"].rename("value").reset_index()
        s = s.rename(columns={"Date": "date"})
        s["risk_factor"] = factor
        s["source"] = f"yfinance:{ticker}"
        s["retrieved_at"] = pd.Timestamp.utcnow()
        frames.append(s[["date", "risk_factor", "value", "source", "retrieved_at"]])
    return pd.concat(frames, ignore_index=True).sort_values(["risk_factor", "date"])


def load_from_csv(path: str | Path, source_label: str = "csv_import") -> pd.DataFrame:
    """Load a local CSV with columns [date, risk_factor, value] (e.g. an
    extract provided by a data team). Adds source/retrieved_at metadata.
    """
    df = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "risk_factor", "value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    df["source"] = source_label
    df["retrieved_at"] = pd.Timestamp.utcnow()
    return df.sort_values(["risk_factor", "date"]).reset_index(drop=True)


def save_raw(df: pd.DataFrame, filename: str | None = None) -> Path:
    """Persist a pull to data/raw/, never overwriting a previous pull."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if filename is None:
        stamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"market_prices_{stamp}.csv"
    out_path = RAW_DIR / filename
    df.to_csv(out_path, index=False)
    return out_path
