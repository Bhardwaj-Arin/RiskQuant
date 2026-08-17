"""Kupiec Proportion-of-Failures test and Christoffersen independence test
(Phase 5).

Kupiec: likelihood-ratio test of whether the observed exception frequency
matches the target frequency implied by the VaR confidence level.

Christoffersen: likelihood-ratio test of whether exceptions are
independent over time (a model can have the "right" exception count but
still fail if exceptions cluster in volatile periods).
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def kupiec_pof_test(n_exceptions: int, n_obs: int, target_rate: float) -> dict:
    """Kupiec (1995) proportion-of-failures likelihood-ratio test.

    H0: true exception probability == target_rate.
    LR_pof = -2 * ln[ (1-p)^(n-x) p^x / (1-x/n)^(n-x) (x/n)^x ]
    ~ chi-square(1) under H0.
    """
    if n_obs == 0:
        raise ValueError("n_obs must be > 0")
    x, n, p = n_exceptions, n_obs, target_rate
    pi_hat = x / n

    def _log_lik(prob: float) -> float:
        # guard against log(0)
        prob = min(max(prob, 1e-10), 1 - 1e-10)
        return (n - x) * np.log(1 - prob) + x * np.log(prob)

    lr = -2 * (_log_lik(p) - _log_lik(pi_hat))
    lr = max(lr, 0.0)
    p_value = 1 - stats.chi2.cdf(lr, df=1)
    return {
        "test": "Kupiec POF",
        "n_obs": n,
        "n_exceptions": x,
        "observed_rate": pi_hat,
        "target_rate": p,
        "lr_statistic": float(lr),
        "p_value": float(p_value),
        "reject_null_at_5pct": bool(p_value < 0.05),
    }


def christoffersen_independence_test(exception_flags: np.ndarray) -> dict:
    """Christoffersen (1998) independence test on a 0/1 exception series.

    Fits a first-order Markov chain to transitions between "exception" and
    "no exception" states and tests whether the transition probability out
    of an exception state equals the transition probability out of a
    no-exception state (independence) via a likelihood-ratio test.
    """
    flags = np.asarray(exception_flags).astype(int)
    if len(flags) < 2:
        raise ValueError("Need at least 2 observations")

    n00 = n01 = n10 = n11 = 0
    for t in range(1, len(flags)):
        prev, curr = flags[t - 1], flags[t]
        if prev == 0 and curr == 0:
            n00 += 1
        elif prev == 0 and curr == 1:
            n01 += 1
        elif prev == 1 and curr == 0:
            n10 += 1
        else:
            n11 += 1

    n0, n1 = n00 + n01, n10 + n11
    pi01 = n01 / n0 if n0 > 0 else 0.0
    pi11 = n11 / n1 if n1 > 0 else 0.0
    pi = (n01 + n11) / (n0 + n1) if (n0 + n1) > 0 else 0.0

    def _safe_log(p, k, n):
        if n == 0:
            return 0.0
        p = min(max(p, 1e-10), 1 - 1e-10)
        return k * np.log(p) + (n - k) * np.log(1 - p)

    log_lik_restricted = _safe_log(pi, n01 + n11, n0 + n1)
    log_lik_unrestricted = _safe_log(pi01, n01, n0) + _safe_log(pi11, n11, n1)

    lr = -2 * (log_lik_restricted - log_lik_unrestricted)
    lr = max(lr, 0.0)
    p_value = 1 - stats.chi2.cdf(lr, df=1)
    return {
        "test": "Christoffersen Independence",
        "n_obs": len(flags),
        "n00": n00, "n01": n01, "n10": n10, "n11": n11,
        "lr_statistic": float(lr),
        "p_value": float(p_value),
        "reject_null_at_5pct": bool(p_value < 0.05),
    }


def conditional_coverage_summary(kupiec_result: dict, christoffersen_result: dict) -> dict:
    """Combined view: a model should have both appropriate exception
    frequency AND reasonably independent exceptions."""
    return {
        "unconditional_coverage_ok": not kupiec_result["reject_null_at_5pct"],
        "independence_ok": not christoffersen_result["reject_null_at_5pct"],
        "overall_pass": (not kupiec_result["reject_null_at_5pct"]) and
                          (not christoffersen_result["reject_null_at_5pct"]),
    }
