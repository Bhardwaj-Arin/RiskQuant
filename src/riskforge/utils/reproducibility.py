"""Reproducibility metadata helpers.

Every experiment should record: configuration, data period, code version,
execution date, model version (blueprint 'Reproducibility' section).
"""
from __future__ import annotations

import datetime as dt
import subprocess
from typing import Any


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return "no-git-repo"


def run_metadata(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "executed_at": dt.datetime.utcnow().isoformat() + "Z",
        "git_commit": get_git_commit(),
        "model_version": config.get("model_version", "unknown"),
        "data_period": f"{config['data']['start_date']} to {config['data']['end_date']}",
        "data_source": config["data"]["source"],
    }
