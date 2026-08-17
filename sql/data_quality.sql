-- Data-quality checks. Educational prototype.

-- 1. Missing calendar dates per risk factor (gaps vs expected trading days
--    are easier to check in pandas; this flags duplicate/missing rows only).
SELECT risk_factor, COUNT(*) AS n_rows,
       COUNT(DISTINCT date) AS n_distinct_dates
FROM market_prices
GROUP BY risk_factor
HAVING COUNT(*) <> COUNT(DISTINCT date);   -- duplicates present

-- 2. Null or non-positive prices (invalid for a level series)
SELECT * FROM market_prices
WHERE value IS NULL OR value <= 0;

-- 3. Stale values: same value repeated for 5+ consecutive calendar days
WITH ordered AS (
    SELECT risk_factor, date, value,
           LAG(value) OVER (PARTITION BY risk_factor ORDER BY date) AS prev_value
    FROM market_prices
)
SELECT * FROM ordered WHERE value = prev_value;

-- 4. Extreme single-day returns (possible outliers/data errors), |return| > 20%
SELECT * FROM risk_factor_returns
WHERE ABS(simple_return) > 0.20;

-- 5. Portfolio weights that do not sum to ~1.0 on a given effective_date
SELECT portfolio_id, effective_date, SUM(weight) AS total_weight
FROM portfolio_positions
GROUP BY portfolio_id, effective_date
HAVING ABS(SUM(weight) - 1.0) > 0.001;
