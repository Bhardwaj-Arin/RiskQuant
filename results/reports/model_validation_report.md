# RiskForge-QRM Model Validation Report

Generated: 2026-08-17T19:01:28.946245Z

**Scope statement:** Educational prototype. Not a production risk engine. Not a claim of Basel/regulatory compliance.

## 1. Model objective
Estimate and validate 1-day portfolio VaR/ES across three competing model families (historical, parametric, EWMA), then stress-test and reverse-stress the same portfolio.

## 2. Data
synthetic data, period 2015-01-01 to 2024-12-31, 13045 raw price rows across 5 risk factors. Data quality PASS = True.

## 3. Assumptions
Confidence=0.99, rolling window=250 days, EWMA lambda=0.94, fixed portfolio weights, linear risk-factor mapping, no rebalancing or transaction costs.

## 4. Implementation
See src/riskforge/{data,portfolio,models,validation,stress,attribution}/ for module-level implementation; tests/ for unit and manual-check verification.

## 5. Test design
Rolling out-of-sample VaR/ES forecasts (strictly backward-looking), Kupiec POF test and Christoffersen independence test per model, multi-start check on the reverse-stress solver.

## 6. Results
      model_id  n_forecasts  n_exceptions  exception_rate  target_rate  avg_exceedance_size  avg_var
historical_var         2358            32        0.013571         0.01             0.003758 0.013907
parametric_var         2358            31        0.013147         0.01             0.004047 0.013186
      ewma_var         2358            37        0.015691         0.01             0.003391 0.012735

## 7. Failures / exceptions observed
- historical_var: overall_pass=True
- parametric_var: overall_pass=True
- ewma_var: overall_pass=False

## 8. Limitations
Synthetic data in this run (no internet access in the build environment) -- must be re-run against real market data before any real interpretation. Linear risk-factor portfolio mapping only (no options/non-linear instruments). Normal-distribution assumption for parametric VaR/ES. No regulatory compliance claim.

## 9. Conclusion
Pipeline runs end-to-end and produces reproducible, testable outputs across VaR/ES modelling, validation, stress and reverse stress, and attribution.

## 10. Recommended next steps
Re-run against real market data via riskforge.data.loader.load_from_yfinance or load_from_csv; extend to a multi-portfolio SQL-backed workflow using sql/schema.sql.