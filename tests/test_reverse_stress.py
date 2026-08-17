import pytest
from riskforge.stress import reverse_stress


WEIGHTS = {"EQUITY_INDEX": 0.45, "RATES_10Y": 0.20, "FX_USD": 0.15, "OIL": 0.10, "GOLD": 0.10}
BOUNDS = {
    "EQUITY_INDEX": (-0.30, 0.0),
    "RATES_10Y": (0.0, 0.03),
    "FX_USD": (-0.15, 0.15),
    "OIL": (-0.25, 0.25),
    "GOLD": (-0.25, 0.25),
}


def test_reverse_stress_reaches_target_loss():
    result = reverse_stress.solve_reverse_stress(WEIGHTS, target_loss=0.10, bounds=BOUNDS)
    assert result["target_reached"]
    assert result["resulting_loss"] >= 0.10 - 1e-6


def test_reverse_stress_respects_bounds():
    result = reverse_stress.solve_reverse_stress(WEIGHTS, target_loss=0.10, bounds=BOUNDS)
    for f, shock in result["shock_vector"].items():
        lo, hi = BOUNDS[f]
        assert lo - 1e-6 <= shock <= hi + 1e-6


def test_verify_solution_agrees_with_solver_output():
    result = reverse_stress.solve_reverse_stress(WEIGHTS, target_loss=0.08, bounds=BOUNDS)
    verification = reverse_stress.verify_solution(WEIGHTS, result["shock_vector"], BOUNDS, 0.08)
    assert verification["verified"]
    assert abs(verification["recomputed_loss"] - result["resulting_loss"]) < 1e-8


def test_infeasible_target_reports_violation():
    # target loss far beyond what bounds can ever produce
    result = reverse_stress.solve_reverse_stress(WEIGHTS, target_loss=5.0, bounds=BOUNDS)
    assert result["constraint_status"] == "VIOLATED"


def test_multi_start_all_reach_target_for_feasible_case():
    df = reverse_stress.multi_start_check(WEIGHTS, target_loss=0.10, bounds=BOUNDS, n_starts=3)
    assert (df["constraint_status"] == "SATISFIED").all()
