"""End-to-end RiskForge-QRM pipeline orchestration script.

Run with:  python scripts/run_pipeline.py

Executes Phases 1-11 of the project blueprint against the offline
synthetic dataset (swap `config["data"]["source"]` and the loader call
for yfinance/CSV once you have real data + internet access) and writes
all tables/figures/reports to results/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from riskforge.utils.config import load_config
from riskforge.utils.reproducibility import run_metadata
from riskforge.data import loader, quality
from riskforge.portfolio import engine as portfolio_engine
from riskforge.models import historical_var, parametric_var, ewma, expected_shortfall
from riskforge.validation import backtest, statistical_tests
from riskforge.stress import scenarios as stress_scenarios
from riskforge.stress import reverse_stress
from riskforge.attribution import attribution
from riskforge.reporting import report


def main():
    print("=" * 70)
    print("RISKFORGE-QRM PIPELINE RUN")
    print("=" * 70)

    config = load_config("base.yaml")
    stress_config = load_config("stress_scenarios.yaml")
    meta = run_metadata(config)
    print("Run metadata:", meta)

    # ---- Phase 1-2: Data + quality -----------------------------------
    print("\n[Phase 1-2] Loading data and running quality checks...")
    prices_long = loader.load_from_synthetic(
        config["data"]["start_date"], config["data"]["end_date"],
        config["data"]["risk_factors"],
    )
    loader.save_raw(prices_long)

    levels_wide = quality.long_to_wide_levels(prices_long)
    returns_wide = quality.levels_to_returns(levels_wide)

    qc_report = quality.run_quality_checks(prices_long, returns_wide)
    print(qc_report.summary())
    report.save_table(qc_report.outlier_returns, "data_quality_outlier_returns")

    # ---- Phase 3: Portfolio -------------------------------------------
    print("\n[Phase 3] Building portfolio...")
    weights = config["portfolio"]["weights"]
    portfolio_engine.validate_weights(weights)
    port_returns = portfolio_engine.portfolio_returns(returns_wide, weights)
    print(f"Portfolio return series: {len(port_returns)} obs, "
          f"mean={port_returns.mean():.5f}, std={port_returns.std():.5f}")

    check = portfolio_engine.manual_check_example()
    manual_result = portfolio_engine.portfolio_returns(check["returns"], check["weights"])
    assert (manual_result.round(6) == check["expected"].round(6)).all(), "Manual check failed!"
    print("Portfolio engine manual verification: PASSED")

    # ---- Phase 4: Risk models (rolling out-of-sample) ------------------
    print("\n[Phase 4] Fitting VaR / ES models (rolling out-of-sample)...")
    confidence = config["risk"]["confidence"]
    window = config["risk"]["window"]

    hvar = historical_var.rolling_historical_var(port_returns, confidence, window)
    pvar = parametric_var.rolling_parametric_var(port_returns, confidence, window)
    evar = ewma.rolling_ewma_var_forecast(port_returns, confidence, config["ewma"]["lambda"], window)
    hes = expected_shortfall.rolling_historical_es(port_returns, confidence, window)

    print(f"Historical VaR: {len(hvar)} forecasts, mean={hvar.mean():.4f}")
    print(f"Parametric VaR: {len(pvar)} forecasts, mean={pvar.mean():.4f}")
    print(f"EWMA VaR:       {len(evar)} forecasts, mean={evar.mean():.4f}")
    print(f"Historical ES:  {len(hes)} forecasts, mean={hes.mean():.4f}")

    # ---- Phase 5: Backtesting & validation -----------------------------
    print("\n[Phase 5] Backtesting and statistical validation...")
    models = {"historical_var": hvar, "parametric_var": pvar, "ewma_var": evar}
    backtest_tables = {}
    stat_results = []
    for name, var_series in models.items():
        table = backtest.build_backtest_table(var_series, port_returns, name)
        backtest_tables[name] = table
        report.save_table(table, f"backtest_{name}")
        report.plot_var_vs_realized(table, name)

        n_exc = int(table["exception_flag"].sum())
        n_obs = len(table)
        kupiec = statistical_tests.kupiec_pof_test(n_exc, n_obs, 1 - confidence)
        christ = statistical_tests.christoffersen_independence_test(table["exception_flag"].values)
        cc = statistical_tests.conditional_coverage_summary(kupiec, christ)
        stat_results.append({"model_id": name, **kupiec, **{f"christ_{k}": v for k, v in christ.items()},
                              **cc})
        print(f"  {name}: exceptions={n_exc}/{n_obs} "
              f"({n_exc/n_obs:.2%} vs target {1-confidence:.2%}), "
              f"Kupiec p={kupiec['p_value']:.3f}, Christoffersen p={christ['p_value']:.3f}, "
              f"overall_pass={cc['overall_pass']}")

    comparison = backtest.compare_models(backtest_tables, confidence)
    report.save_table(comparison.reset_index(), "model_comparison")
    report.save_table(pd.DataFrame(stat_results), "statistical_tests")
    report.plot_model_comparison(comparison)

    # ---- Phase 6: Stress testing ---------------------------------------
    print("\n[Phase 6] Stress testing...")
    scenario_results = stress_scenarios.run_scenario_set(weights, stress_config["scenarios"])
    report.save_table(scenario_results, "stress_scenarios")
    report.plot_stress_scenarios(scenario_results)

    worst_day = stress_scenarios.historical_worst_day_scenario(returns_wide, weights)
    print(f"  Historical worst day: {worst_day['date'].date()}, "
          f"loss={worst_day['portfolio_loss']:.2%}")

    sens = stress_scenarios.sensitivity_analysis(
        weights, "EQUITY_INDEX", [round(x, 2) for x in [-0.3, -0.2, -0.1, 0.0, 0.1]]
    )
    report.save_table(sens, "sensitivity_equity")

    # ---- Phase 7: Reverse stress testing --------------------------------
    print("\n[Phase 7] Reverse stress testing...")
    bounds = {k: tuple(v) for k, v in config["stress"]["bounds"].items()}
    rs_result = reverse_stress.solve_reverse_stress(weights, config["stress"]["target_loss"], bounds)
    verification = reverse_stress.verify_solution(
        weights, rs_result["shock_vector"], bounds, config["stress"]["target_loss"]
    )
    print(f"  Target loss: {config['stress']['target_loss']:.1%}, "
          f"resulting loss: {rs_result['resulting_loss']:.2%}, "
          f"status: {rs_result['constraint_status']}, verified={verification['verified']}")
    print(f"  Minimum-norm shock vector: "
          f"{ {k: round(v,4) for k,v in rs_result['shock_vector'].items()} }")

    multi_start = reverse_stress.multi_start_check(weights, config["stress"]["target_loss"], bounds)
    report.save_table(multi_start, "reverse_stress_multi_start")
    rs_row = pd.DataFrame([{
        "risk_factor": f, "shock": v, "resulting_loss": rs_result["resulting_loss"],
        "target_loss": rs_result["target_loss"], "constraint_status": rs_result["constraint_status"],
    } for f, v in rs_result["shock_vector"].items()])
    report.save_table(rs_row, "reverse_stress_solution")

    # ---- Phase 8: Risk attribution ---------------------------------------
    print("\n[Phase 8] Risk attribution...")
    cov = portfolio_engine.sample_covariance(returns_wide)
    vol_contrib = attribution.volatility_contribution(weights, cov)
    report.save_table(vol_contrib, "attribution_volatility")
    print(vol_contrib.to_string(index=False))

    factor_ranking = attribution.factor_ranking_across_scenarios(scenario_results)
    report.save_table(factor_ranking, "attribution_scenario_ranking")

    # ---- Phase 11: Reporting ---------------------------------------------
    print("\n[Phase 11] Writing model validation report...")
    context = {
        "objective": "Estimate and validate 1-day portfolio VaR/ES across three "
                      "competing model families (historical, parametric, EWMA), "
                      "then stress-test and reverse-stress the same portfolio.",
        "data_summary": f"{meta['data_source']} data, period {meta['data_period']}, "
                          f"{len(prices_long)} raw price rows across "
                          f"{prices_long['risk_factor'].nunique()} risk factors. "
                          f"Data quality PASS = {qc_report.passed}.",
        "assumptions": f"Confidence={confidence}, rolling window={window} days, "
                         f"EWMA lambda={config['ewma']['lambda']}, fixed portfolio weights, "
                         f"linear risk-factor mapping, no rebalancing or transaction costs.",
        "implementation": "See src/riskforge/{data,portfolio,models,validation,stress,"
                            "attribution}/ for module-level implementation; tests/ for "
                            "unit and manual-check verification.",
        "test_design": "Rolling out-of-sample VaR/ES forecasts (strictly backward-looking), "
                         "Kupiec POF test and Christoffersen independence test per model, "
                         "multi-start check on the reverse-stress solver.",
        "results_summary": comparison.reset_index().to_string(index=False),
        "failures": "\n".join(
            f"- {r['model_id']}: overall_pass={r['overall_pass']}" for r in stat_results
        ),
        "limitations": "Synthetic data in this run (no internet access in the build "
                          "environment) -- must be re-run against real market data before "
                          "any real interpretation. Linear risk-factor portfolio mapping "
                          "only (no options/non-linear instruments). Normal-distribution "
                          "assumption for parametric VaR/ES. No regulatory compliance claim.",
        "conclusion": "Pipeline runs end-to-end and produces reproducible, testable "
                        "outputs across VaR/ES modelling, validation, stress and reverse "
                        "stress, and attribution.",
        "next_steps": "Re-run against real market data via riskforge.data.loader."
                         "load_from_yfinance or load_from_csv; extend to a multi-portfolio "
                         "SQL-backed workflow using sql/schema.sql.",
    }
    report_path = report.write_model_validation_report(context)
    print(f"  Report written to {report_path}")

    print("\n" + "=" * 70)
    print("PIPELINE RUN COMPLETE. See results/tables, results/figures, results/reports.")
    print("=" * 70)


if __name__ == "__main__":
    main()
