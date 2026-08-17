-- Result-retrieval and audit queries. Educational prototype.

-- Latest VaR / ES per model for a portfolio
SELECT r.model_id, r.forecast_date, r.var, r.expected_shortfall
FROM risk_results r
JOIN (
    SELECT model_id, MAX(forecast_date) AS max_date
    FROM risk_results
    WHERE portfolio_id = :portfolio_id
    GROUP BY model_id
) latest
ON r.model_id = latest.model_id AND r.forecast_date = latest.max_date
WHERE r.portfolio_id = :portfolio_id;

-- Exception rate per model over the full backtest window
SELECT model_id,
       COUNT(*) FILTER (WHERE exception_flag) AS n_exceptions,
       COUNT(*) AS n_forecasts,
       ROUND(COUNT(*) FILTER (WHERE exception_flag)::numeric / COUNT(*), 4) AS exception_rate
FROM backtest_results
GROUP BY model_id
ORDER BY model_id;

-- Worst stress scenarios by portfolio loss
SELECT scenario_id, SUM(portfolio_loss) AS total_scenario_loss
FROM stress_results
GROUP BY scenario_id
ORDER BY total_scenario_loss DESC;

-- Reverse-stress runs that satisfied constraints, smallest shock norm first
-- (norm computed in Python; this just filters feasible runs for review)
SELECT run_id, risk_factor, shock, resulting_loss
FROM reverse_stress_results
WHERE constraint_status = 'SATISFIED'
ORDER BY run_id, risk_factor;
