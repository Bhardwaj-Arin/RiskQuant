"""Configuration loading utilities.

Design principle (from the project blueprint): parameters live in
configs/*.yaml, not scattered as magic numbers across modules.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIGS_DIR = REPO_ROOT / "configs"


def load_config(name: str = "base.yaml") -> dict[str, Any]:
    """Load a YAML config file from configs/.

    Parameters
    ----------
    name: filename inside configs/, e.g. "base.yaml" or "stress_scenarios.yaml"
    """
    path = CONFIGS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)
