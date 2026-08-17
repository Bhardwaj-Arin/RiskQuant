# Dashboard improvements

## Version: Interview-ready visual redesign

### Fixed
- Fixed the VaR backtest error caused by `bt.var * 100`; the correct column access is `bt["var"] * 100`.

### Improved
- Replaced table-first presentation with visual cards, scorecards and explanatory callouts.
- Added a project-story landing page that explains the entire modelling workflow.
- Added interactive model comparison against the 1% target.
- Added Plotly range selector/range slider to the backtest chart.
- Added visual validation verdicts for Kupiec and Christoffersen tests.
- Added stress-scenario leaderboard and factor-contribution heatmap.
- Added equity-shock sensitivity chart with simple interpretation.
- Added reverse-stress shock visualisation and multi-start stability chart.
- Added factor variance-contribution chart and scenario contribution ranking.
- Moved raw dataframes behind expanders to reduce visual clutter.
- Added a methodology/concepts page focused on explainable statistics and quantitative-risk fundamentals.
- Kept the dashboard presentation-only; no core risk formulas were moved into Streamlit.
