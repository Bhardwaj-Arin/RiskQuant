-- RiskForge-QRM PostgreSQL schema
-- Educational prototype schema. Not a production risk-data model.

CREATE TABLE IF NOT EXISTS market_prices (
    date            DATE            NOT NULL,
    risk_factor     VARCHAR(32)     NOT NULL,
    value           DOUBLE PRECISION NOT NULL,
    source          VARCHAR(64)     NOT NULL,
    retrieved_at    TIMESTAMP       NOT NULL DEFAULT now(),
    PRIMARY KEY (date, risk_factor)
);

CREATE TABLE IF NOT EXISTS risk_factor_returns (
    date            DATE            NOT NULL,
    risk_factor     VARCHAR(32)     NOT NULL,
    simple_return   DOUBLE PRECISION,
    log_return      DOUBLE PRECISION,
    PRIMARY KEY (date, risk_factor)
);

CREATE TABLE IF NOT EXISTS portfolio_positions (
    portfolio_id    VARCHAR(64)     NOT NULL,
    risk_factor     VARCHAR(32)     NOT NULL,
    weight          DOUBLE PRECISION NOT NULL,
    effective_date  DATE            NOT NULL,
    PRIMARY KEY (portfolio_id, risk_factor, effective_date)
);

CREATE TABLE IF NOT EXISTS model_config (
    model_id        VARCHAR(64)     NOT NULL,
    confidence      DOUBLE PRECISION,
    window_size     INTEGER,
    parameter_name  VARCHAR(64)     NOT NULL,
    parameter_value DOUBLE PRECISION,
    version         VARCHAR(16)     NOT NULL,
    PRIMARY KEY (model_id, parameter_name, version)
);

CREATE TABLE IF NOT EXISTS risk_results (
    forecast_date       DATE            NOT NULL,
    portfolio_id        VARCHAR(64)     NOT NULL,
    model_id            VARCHAR(64)     NOT NULL,
    var                 DOUBLE PRECISION NOT NULL,
    expected_shortfall  DOUBLE PRECISION,
    PRIMARY KEY (forecast_date, portfolio_id, model_id)
);

CREATE TABLE IF NOT EXISTS backtest_results (
    forecast_date   DATE            NOT NULL,
    model_id        VARCHAR(64)     NOT NULL,
    var             DOUBLE PRECISION NOT NULL,
    realized_pnl    DOUBLE PRECISION NOT NULL,
    exception_flag  BOOLEAN         NOT NULL,
    PRIMARY KEY (forecast_date, model_id)
);

CREATE TABLE IF NOT EXISTS stress_results (
    scenario_id     VARCHAR(64)     NOT NULL,
    risk_factor     VARCHAR(32)     NOT NULL,
    shock           DOUBLE PRECISION NOT NULL,
    portfolio_loss  DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (scenario_id, risk_factor)
);

CREATE TABLE IF NOT EXISTS reverse_stress_results (
    run_id              VARCHAR(64)     NOT NULL,
    target_loss         DOUBLE PRECISION NOT NULL,
    risk_factor         VARCHAR(32)     NOT NULL,
    shock               DOUBLE PRECISION NOT NULL,
    resulting_loss      DOUBLE PRECISION NOT NULL,
    constraint_status   VARCHAR(32)     NOT NULL,
    PRIMARY KEY (run_id, risk_factor)
);
