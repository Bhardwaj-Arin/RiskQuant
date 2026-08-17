"""Reverse stress testing (Phase 7) -- the project's signature feature.

Normal stress: "what happens if equity falls 20%?"
Reverse stress: "what is the smallest combination of shocks sufficient to
cause a target portfolio loss?"

Formulated as:
    minimize   ||delta_x||_2
    subject to Loss(delta_x) >= target_loss
               lower_bound <= delta_x <= upper_bound

This finds *a* minimum-norm feasible scenario under the project's linear
portfolio model and stated bounds -- not "the true worst-case market
scenario" (see docs/ for the exact non-overclaiming language to use).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize, NonlinearConstraint


def solve_reverse_stress(
    weights: dict[str, float],
    target_loss: float,
    bounds: dict[str, tuple[float, float]],
    x0: dict[str, float] | None = None,
) -> dict:
    """Solve for the minimum-norm shock vector that reaches target_loss.

    Loss(delta_x) = -sum_i w_i * delta_x_i  (portfolio loss, positive = bad)
    Constraint: Loss(delta_x) >= target_loss
    """
    factors = list(weights.keys())
    w = np.array([weights[f] for f in factors])
    lb = np.array([bounds[f][0] for f in factors])
    ub = np.array([bounds[f][1] for f in factors])

    if x0 is None:
        x0_arr = np.clip(np.zeros(len(factors)), lb, ub)
    else:
        x0_arr = np.array([x0.get(f, 0.0) for f in factors])

    def objective(x):
        return np.sum(x ** 2)  # minimize squared L2 norm (smooth, equiv. minimizer to L2 norm)

    def loss_fn(x):
        return -np.dot(w, x)  # portfolio loss

    constraint = NonlinearConstraint(loss_fn, target_loss, np.inf)
    result = minimize(
        objective, x0_arr, method="SLSQP",
        bounds=list(zip(lb, ub)),
        constraints=[constraint],
        options={"maxiter": 500, "ftol": 1e-10},
    )

    shock_vector = dict(zip(factors, result.x))
    resulting_loss = float(loss_fn(result.x))
    constraints_satisfied = bool(np.all(result.x >= lb - 1e-6) and np.all(result.x <= ub + 1e-6))
    target_reached = resulting_loss >= target_loss - 1e-6

    return {
        "success": bool(result.success),
        "shock_vector": shock_vector,
        "resulting_loss": resulting_loss,
        "target_loss": target_loss,
        "target_reached": target_reached,
        "constraints_satisfied": constraints_satisfied,
        "constraint_status": "SATISFIED" if (constraints_satisfied and target_reached) else "VIOLATED",
        "l2_norm": float(np.sqrt(np.sum(result.x ** 2))),
        "solver_message": result.message,
    }


def verify_solution(weights: dict[str, float], shock_vector: dict[str, float],
                     bounds: dict[str, tuple[float, float]], target_loss: float) -> dict:
    """Independent re-check of a reverse-stress solution (blueprint Phase 7:
    'verify constraints', 'verify target')."""
    loss = -sum(weights[f] * shock_vector[f] for f in shock_vector)
    bounds_ok = all(bounds[f][0] - 1e-6 <= shock_vector[f] <= bounds[f][1] + 1e-6 for f in shock_vector)
    target_ok = loss >= target_loss - 1e-6
    return {"recomputed_loss": loss, "bounds_ok": bounds_ok, "target_ok": target_ok,
            "verified": bounds_ok and target_ok}


def multi_start_check(weights: dict[str, float], target_loss: float,
                       bounds: dict[str, tuple[float, float]], n_starts: int = 5,
                       seed: int = 7) -> pd.DataFrame:
    """Rerun the solver from several random feasible starting points to
    report whether the solution looks stable/unique or merely one feasible
    minimum (blueprint: 'test alternative starting points if non-convex';
    report uniqueness honestly)."""
    rng = np.random.default_rng(seed)
    factors = list(weights.keys())
    rows = []
    for i in range(n_starts):
        x0 = {f: rng.uniform(*bounds[f]) for f in factors}
        result = solve_reverse_stress(weights, target_loss, bounds, x0=x0)
        rows.append({"start": i, "l2_norm": result["l2_norm"],
                      "constraint_status": result["constraint_status"],
                      **{f"shock_{f}": result["shock_vector"][f] for f in factors}})
    return pd.DataFrame(rows)
