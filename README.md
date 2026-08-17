# RiskForge-QRM

**Quantitative Market Risk Modelling, Validation & Reverse Stress Testing Framework**

RiskForge-QRM is an educational quantitative market-risk framework that
implements a complete risk-modelling and model-validation workflow.

The project estimates portfolio risk using multiple VaR models, validates
their forecasts against realised losses, evaluates extreme scenarios through
stress testing, solves reverse-stress problems, and attributes portfolio risk
to individual risk factors.

### 🚀 Interactive Dashboard

**Live Demo:** ADD-YOUR-STREAMLIT-URL-HERE

**GitHub:** ADD-YOUR-GITHUB-URL-HERE

The Streamlit dashboard allows users to explore the complete project without
opening the source code.

### Project workflow

Market Data
↓
Data Quality
↓
Portfolio Construction
↓
Historical VaR
↓
Parametric VaR
↓
EWMA VaR
↓
Expected Shortfall
↓
Backtesting
↓
Stress Testing
↓
Reverse Stress Testing
↓
Risk Attribution
↓
Model Validation


> **Scope statement.** This is an educational prototype, **not** a
> production bank risk engine and **not** a regulatory capital calculator.
> Basel/BIS concepts are used as learning references; nothing here claims
> regulatory compliance.

> **Note on the JD.** UBS's QRM-Mumbai posting centers on *credit exposure
> measures* for the banking and trading book. This project is a
> *market-risk* framework (VaR/ES/backtesting/stress) — it demonstrates
> the same underlying skill set (stats, model validation, Python, SQL)
> the JD asks for, but it does not attempt counterparty/credit-exposure
> modelling (PFE, EAD). Worth saying explicitly in an interview.

## What it does

1. Generates/ingests risk-factor price data (synthetic by default;
   `yfinance` or CSV for real data — see `src/riskforge/data/loader.py`)
2. Runs data-quality checks (duplicates, missing values, date gaps, stale
   values, outlier returns)
3. Builds a fixed-weight portfolio return/P&L series
4. Fits three competing 1-day VaR models — Historical, Parametric
   (variance-covariance), EWMA-volatility — plus historical Expected
   Shortfall, all as **rolling, strictly out-of-sample forecasts** (no
   look-ahead bias)
5. Backtests every model: exception rate, **Kupiec proportion-of-failures
   test**, **Christoffersen independence test**, model comparison
6. Runs historical, hypothetical, sensitivity and multi-factor **stress
   tests**
7. Solves a **reverse stress test** — "what is the smallest combination of
   market shocks that would cause a 10% portfolio loss?" — as a
   constrained optimization problem, with an independent verification and
   multi-start stability check
8. Runs **risk attribution** (variance decomposition + scenario factor
   ranking)
9. Writes reproducible CSV tables, figures, and a structured **model
   validation report** to `results/`

## Repository structure

```
RiskForge-QRM/
├── configs/            # all parameters — nothing hardcoded in code
├── data/{raw,interim,processed}/
├── sql/                # PostgreSQL schema + data-quality/result queries
├── src/riskforge/
│   ├── data/            # loading (synthetic/yfinance/csv) + quality checks
│   ├── portfolio/        # risk-factor -> portfolio return/P&L engine
│   ├── models/           # historical/parametric/EWMA VaR, ES
│   ├── validation/       # backtesting harness, Kupiec, Christoffersen
│   ├── stress/           # scenario engine + reverse-stress optimizer
│   ├── attribution/      # variance decomposition, scenario ranking
│   ├── reporting/        # tables, figures, validation report writer
│   └── utils/            # config loading, run metadata
├── scripts/run_pipeline.py   # end-to-end orchestration
├── tests/               # pytest unit + manual-check tests (36 tests)
├── results/{tables,figures,reports}/
└── dashboard/app.py      # optional Streamlit presentation layer
```

## Interactive dashboard

The Streamlit presentation layer has an interview-oriented visual dashboard with an executive overview, interactive VaR model comparison, backtesting/validation, stress testing, reverse stress, risk attribution, and methodology/assumptions pages. See `dashboard/README.md`.

## Dashboard Preview

### Project Story

![Project Story](docs/screenshots/overview.png)

### VaR Model Lab

![VaR Model Lab](docs/screenshots/var-model-lab.png)

### Backtesting & Validation

![Backtesting](docs/screenshots/backtesting.png)

### Stress Testing

![Stress Testing](docs/screenshots/stress-testing.png)

### Reverse Stress

![Reverse Stress](docs/screenshots/reverse-stress.png)

### Risk Attribution

![Risk Attribution](docs/screenshots/risk-attribution.png)

## Key Results

The reference run compares three 1-day VaR models at a 99% confidence
level.

| Model | Exception Rate | Target | Exceptions |
|---|---:|---:|---:|
| Historical VaR | 1.357% | 1.0% | 32 |
| Parametric VaR | 1.315% | 1.0% | 31 |
| EWMA VaR | 1.569% | 1.0% | 37 |

The project also performs:

- Kupiec proportion-of-failures testing
- Christoffersen independence testing
- Stress testing
- Reverse stress testing
- Risk attribution
- Multi-start stability checking

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# run the full pipeline (synthetic data — works offline)
python scripts/run_pipeline.py

# run the test suite
pytest

# optional dashboard
streamlit run dashboard/app.py
```

## Using real market data instead of synthetic

The included run uses `riskforge.data.loader.load_from_synthetic(...)` —
a fat-tailed, volatility-clustered, correlated synthetic dataset, clearly
tagged `source='synthetic'` everywhere it appears — because this was built
in an offline environment. Swap one line in `scripts/run_pipeline.py`:

```python
# instead of:
prices_long = loader.load_from_synthetic(start, end, factors)
# use:
prices_long = loader.load_from_yfinance(
    {"EQUITY_INDEX": "^GSPC", "RATES_10Y": "^TNX", "FX_USD": "DX-Y.NYB",
     "OIL": "CL=F", "GOLD": "GC=F"},
    start, end,
)
```
or `loader.load_from_csv(path)` for a provided data extract. **Do not
present synthetic-data results as real market findings** — rerun against
real data before drawing conclusions.

## Model comparison, this run

See `results/tables/model_comparison.csv` and
`results/reports/model_validation_report.md` for the exact numbers from
the last pipeline run. In the reference synthetic run, all three models
land close to their 1% target exception rate; the EWMA model's exception
clustering was flagged by the Christoffersen test as a genuine, documented
model-validation finding (not hidden) — see the report's "Failures /
exceptions observed" section, and the interview notes on how to talk
about it.

## What this project deliberately does not include

No deep learning, no LLM chatbot, no Monte Carlo counterparty-credit
simulator, no giant list of ML models, no claim of Basel regulatory
compliance, no fake performance numbers. The goal is a project every
formula and design decision in which can be explained on a whiteboard.

## Definition of done

- [x] Every core model has unit tests (36 tests, `tests/`)
- [x] Data-quality checks run and pass
- [x] Rolling out-of-sample evaluation (no look-ahead bias)
- [x] VaR exceptions measured; two backtests implemented (Kupiec, Christoffersen)
- [x] Stress and reverse-stress outputs reproducible and independently verified
- [x] Model comparison documented
- [x] Assumptions and limitations explicit (`results/reports/model_validation_report.md`)
- [x] Results stored as CSV/figures
- [x] README explains methodology
- [x] Technical model-validation report exists
- [ ] SQL layer wired to a live PostgreSQL instance (`sql/schema.sql` ready; not yet connected to the Python pipeline)
- [ ] Real market data run (synthetic only, pending internet access)

## Sources / industry alignment

Basel's market-risk framework uses Expected Shortfall within its
internal-model approach and includes backtesting, stress testing and
model-governance considerations; BIS guidance defines reverse stress
testing as starting from a predefined adverse outcome and solving
backward for scenarios that could produce it. These motivate this
project's architecture without implying regulatory compliance.
