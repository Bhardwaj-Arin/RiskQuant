import numpy as np
import pandas as pd
from riskforge.validation import backtest, statistical_tests


def test_build_backtest_table_flags_correct_exceptions():
    dates = pd.bdate_range("2024-01-01", periods=5)
    var = pd.Series([0.02, 0.02, 0.02, 0.02, 0.02], index=dates)
    realized = pd.Series([0.01, -0.05, 0.00, -0.01, -0.03], index=dates)  # losses: -0.01,0.05,0.00,0.01,0.03
    table = backtest.build_backtest_table(var, realized, "test_model")
    # exception where realized_loss > var: day2 (0.05>0.02) and day5 (0.03>0.02)
    assert table["exception_flag"].sum() == 2
    assert backtest.exception_rate(table) == 0.4


def test_kupiec_test_does_not_reject_when_rate_matches_target():
    # 250 obs, exactly 1% exceptions (target for 99% VaR)
    result = statistical_tests.kupiec_pof_test(n_exceptions=3, n_obs=250, target_rate=0.01)
    assert result["p_value"] > 0.05
    assert result["reject_null_at_5pct"] is False


def test_kupiec_test_rejects_when_rate_far_from_target():
    # Way too many exceptions relative to a 1% target
    result = statistical_tests.kupiec_pof_test(n_exceptions=40, n_obs=250, target_rate=0.01)
    assert result["reject_null_at_5pct"] is True


def test_christoffersen_detects_clustering():
    # Exceptions clustered together (violates independence)
    flags = np.array([0]*20 + [1,1,1,1,1] + [0]*20)
    result = statistical_tests.christoffersen_independence_test(flags)
    assert result["lr_statistic"] > 0


def test_christoffersen_does_not_flag_scattered_exceptions():
    rng = np.random.default_rng(0)
    flags = (rng.uniform(size=500) < 0.01).astype(int)  # scattered ~1% exceptions
    result = statistical_tests.christoffersen_independence_test(flags)
    # scattered, low-rate exceptions should generally not show strong clustering
    assert result["p_value"] > 0.01


def test_compare_models_summary_columns():
    dates = pd.bdate_range("2024-01-01", periods=10)
    var = pd.Series(0.02, index=dates)
    realized = pd.Series(np.random.default_rng(0).normal(0, 0.015, 10), index=dates)
    table = backtest.build_backtest_table(var, realized, "m1")
    comparison = backtest.compare_models({"m1": table}, confidence=0.99)
    assert "exception_rate" in comparison.columns
    assert "target_rate" in comparison.columns
