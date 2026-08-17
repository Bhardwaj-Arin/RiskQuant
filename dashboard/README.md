# RiskForge-QRM — Interactive Streamlit Dashboard

The dashboard is designed as an **interview-friendly market-risk story**, not as a collection of raw tables.

## Main design goals

- Make the project understandable from the dashboard alone
- Prefer visual explanations over raw dataframes
- Keep the mathematics within the project's existing syllabus
- Use interactive Plotly charts where interaction adds value
- Keep the Streamlit layer presentation-only; core risk calculations remain in `src/riskforge/`
- Make assumptions and limitations visible

## Pages

1. **Project Story** — explains the full workflow and the key findings in one place.
2. **VaR Model Lab** — compares Historical, Parametric and EWMA VaR and provides an interactive realised-loss vs VaR explorer.
3. **Backtesting** — explains exception rates, Kupiec POF and Christoffersen independence testing using visual verdict cards.
4. **Stress Testing** — ranks scenarios, shows factor contributions as a heatmap, and provides an equity-shock sensitivity view.
5. **Reverse Stress** — visualises the shock vector required to reach the target loss and shows multi-start stability.
6. **Risk Attribution** — explains variance contribution and scenario contribution ranking.
7. **Methodology** — documents the modelling assumptions, concepts and limitations in simple language.

Raw CSV tables are kept behind expandable sections so the default experience is visual and readable.

## Run

From the project root:

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
python -m streamlit run dashboard/app.py
```

## Important implementation note

When reading the backtest CSV, the VaR column is accessed as `bt["var"]` rather than `bt.var`. In pandas, `bt.var` resolves to the DataFrame's built-in variance method, which caused the previous dashboard's `unsupported operand type(s) for *: 'method' and 'int'` error.
