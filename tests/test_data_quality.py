import pandas as pd
import pytest
from riskforge.data import quality, synthetic


@pytest.fixture
def sample_prices():
    return synthetic.generate_market_prices("2020-01-01", "2020-06-30", seed=1)


def test_no_duplicates_in_clean_synthetic_data(sample_prices):
    dups = quality.check_duplicates(sample_prices)
    assert dups.empty


def test_no_missing_values_in_clean_synthetic_data(sample_prices):
    missing = quality.check_missing_values(sample_prices)
    assert missing.empty


def test_duplicate_detection_catches_injected_duplicate(sample_prices):
    dirty = pd.concat([sample_prices, sample_prices.iloc[[0]]], ignore_index=True)
    dups = quality.check_duplicates(dirty)
    assert len(dups) == 2  # the original + the injected copy


def test_missing_value_detection_catches_injected_null(sample_prices):
    dirty = sample_prices.copy()
    dirty.loc[0, "value"] = None
    missing = quality.check_missing_values(dirty)
    assert len(missing) == 1


def test_stale_value_detection_catches_injected_flatline(sample_prices):
    dirty = sample_prices.copy()
    factor_mask = dirty["risk_factor"] == dirty["risk_factor"].iloc[0]
    idx = dirty[factor_mask].index[:6]
    dirty.loc[idx, "value"] = 100.0
    stale = quality.check_stale_values(dirty, min_run=5)
    assert len(stale) >= 1


def test_long_to_wide_and_returns_roundtrip(sample_prices):
    wide = quality.long_to_wide_levels(sample_prices)
    returns = quality.levels_to_returns(wide)
    assert len(returns) == len(wide) - 1
    assert set(returns.columns) == set(wide.columns)
