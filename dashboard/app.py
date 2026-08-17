"""RiskForge-QRM | Interactive Market Risk Dashboard.

Presentation layer only: reads artefacts produced by scripts/run_pipeline.py.
No core risk formulas are implemented here.

Run from the project root:
    python -m streamlit run dashboard/app.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CONFIGS = ROOT / "configs"

st.set_page_config(
    page_title="RiskForge-QRM | Market Risk Lab",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Visual theme
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
:root {
    --bg: #070b16;
    --panel: #0d1424;
    --panel2: #111a2d;
    --border: rgba(255,255,255,.09);
    --text: #f4f7ff;
    --muted: #96a3bd;
    --purple: #8b7cff;
    --cyan: #36d7d0;
    --orange: #ffb454;
    --red: #ff647c;
    --green: #43d39e;
}
.stApp {
    background:
      radial-gradient(900px 500px at 92% -5%, rgba(139,124,255,.16), transparent 62%),
      radial-gradient(700px 450px at -10% 20%, rgba(54,215,208,.07), transparent 65%),
      var(--bg);
    color: var(--text);
}
[data-testid="stHeader"] { background: rgba(7,11,22,.72); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1120 0%, #070b16 100%);
    border-right: 1px solid var(--border);
}
.block-container { max-width: 1480px; padding-top: 1.15rem; padding-bottom: 4rem; }

/* Hide default Streamlit radio circles so the sidebar reads like navigation. */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display:none; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 10px; padding: 9px 10px; margin: 2px 0;
    color: #aeb9d0; transition: .15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(139,124,255,.08); color: white; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(139,124,255,.18), rgba(139,124,255,.05));
    color: white; border: 1px solid rgba(139,124,255,.20);
}

.rf-eyebrow { color: var(--cyan); font-size: .72rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
.rf-title { font-size: 2.65rem; line-height: 1.02; font-weight: 850; margin: .2rem 0 .55rem; letter-spacing: -.03em; }
.rf-subtitle { color: var(--muted); font-size: 1rem; line-height: 1.55; max-width: 960px; }
.rf-hero {
    padding: 28px 30px; border: 1px solid rgba(139,124,255,.22); border-radius: 24px;
    background: linear-gradient(135deg, rgba(17,26,45,.94), rgba(13,18,34,.92));
    box-shadow: 0 25px 70px rgba(0,0,0,.22); margin-bottom: 18px;
}
.rf-hero h2 { margin: 0 0 8px; font-size: 1.75rem; }
.rf-hero p { margin: 0; color: #aeb9d0; line-height: 1.6; }
.rf-card {
    background: linear-gradient(145deg, rgba(17,26,45,.96), rgba(10,16,29,.96));
    border: 1px solid var(--border); border-radius: 18px; padding: 18px 19px;
    height: 100%; box-shadow: 0 14px 35px rgba(0,0,0,.13);
}
.rf-card h3 { margin: 0 0 7px; font-size: 1.02rem; color: var(--text); }
.rf-card p { margin: 0; color: var(--muted); line-height: 1.5; font-size: .9rem; }
.rf-card .small { font-size: .78rem; color: #77839d; margin-top: 10px; }
.rf-metric {
    background: linear-gradient(145deg, #111a2d, #0b1221); border: 1px solid var(--border);
    border-radius: 16px; padding: 15px 17px; min-height: 104px;
}
.rf-metric-label { color: #8794ad; font-size: .70rem; font-weight: 800; letter-spacing: .10em; text-transform: uppercase; }
.rf-metric-value { color: var(--text); font-size: 1.72rem; font-weight: 850; margin-top: 5px; }
.rf-metric-help { color: #71809b; font-size: .76rem; margin-top: 4px; line-height: 1.35; }
.rf-section { margin-top: 1.45rem; margin-bottom: .75rem; }
.rf-section-title { font-size: 1.35rem; font-weight: 820; margin-bottom: 3px; }
.rf-section-copy { color: var(--muted); font-size: .88rem; line-height: 1.5; }
.rf-pill { display:inline-block; padding: 4px 9px; border-radius: 999px; font-size:.7rem; font-weight:800; margin-right:5px; }
.purple { color:#c7bdff; background:rgba(139,124,255,.12); border:1px solid rgba(139,124,255,.22); }
.green { color:#6ce8b8; background:rgba(67,211,158,.10); border:1px solid rgba(67,211,158,.18); }
.red { color:#ff91a1; background:rgba(255,100,124,.10); border:1px solid rgba(255,100,124,.18); }
.orange { color:#ffd08a; background:rgba(255,180,84,.10); border:1px solid rgba(255,180,84,.18); }
.rf-step { min-height: 150px; }
.rf-step-num { width: 34px; height: 34px; border-radius: 10px; display:flex; align-items:center; justify-content:center; background:rgba(139,124,255,.12); color:#c6bdff; font-weight:850; margin-bottom:14px; }
.rf-takeaway { border-left: 3px solid var(--cyan); padding: 13px 16px; background: rgba(54,215,208,.055); border-radius: 0 12px 12px 0; color:#c8d3e9; line-height:1.55; }
.rf-takeaway b { color:#f5f8ff; }
.rf-model { border-top: 3px solid var(--purple); }
.rf-model.orange-top { border-top-color: var(--orange); }
.rf-model.cyan-top { border-top-color: var(--cyan); }
.rf-big { font-size: 2.3rem; font-weight: 900; letter-spacing:-.03em; }
.rf-center { text-align:center; }
.stButton button { border-radius: 10px; }
[data-testid="stDataFrame"] { border-radius: 12px; }
details { border-color: var(--border) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame | None:
    path = RESULTS / "tables" / f"{name}.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)

comparison = load_csv("model_comparison")
stats = load_csv("statistical_tests")
stress = load_csv("stress_scenarios")
reverse = load_csv("reverse_stress_solution")
reverse_multi = load_csv("reverse_stress_multi_start")
vol = load_csv("attribution_volatility")
scenario_rank = load_csv("attribution_scenario_ranking")
sensitivity = load_csv("sensitivity_equity")

confidence, window, ewma_lambda, target_loss = .99, 250, .94, .10
weights = {"EQUITY_INDEX": .45, "RATES_10Y": .20, "FX_USD": .15, "OIL": .10, "GOLD": .10}
try:
    import yaml
    cfg = yaml.safe_load((CONFIGS / "base.yaml").read_text(encoding="utf-8"))
    confidence = float(cfg["risk"]["confidence"])
    window = int(cfg["risk"]["window"])
    ewma_lambda = float(cfg["ewma"]["lambda"])
    target_loss = float(cfg["stress"]["target_loss"])
    weights = cfg["portfolio"]["weights"]
except Exception:
    pass

if comparison is None:
    st.error("Results are not available. Run `python scripts/run_pipeline.py` from the project root.")
    st.stop()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
MODEL_NAMES = {
    "historical_var": "Historical VaR",
    "parametric_var": "Parametric VaR",
    "ewma_var": "EWMA VaR",
}


def friendly_model(x: str) -> str:
    return MODEL_NAMES.get(str(x), str(x).replace("_", " ").title())


def metric_card(label: str, value: str, help_text: str = "") -> None:
    st.markdown(
        f"<div class='rf-metric'><div class='rf-metric-label'>{label}</div>"
        f"<div class='rf-metric-value'>{value}</div><div class='rf-metric-help'>{help_text}</div></div>",
        unsafe_allow_html=True,
    )


def section(title: str, copy: str = "") -> None:
    st.markdown(
        f"<div class='rf-section'><div class='rf-section-title'>{title}</div>"
        f"<div class='rf-section-copy'>{copy}</div></div>", unsafe_allow_html=True
    )


def card(title: str, copy: str, extra_class: str = "") -> None:
    st.markdown(
        f"<div class='rf-card {extra_class}'><h3>{title}</h3><p>{copy}</p></div>",
        unsafe_allow_html=True,
    )


def chart(fig: go.Figure, height: int = 410) -> None:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=12, r=16, t=55, b=25),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dfe7f7"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="#111a2d", font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.07)", zeroline=False)
    st.plotly_chart(fig, use_container_width=True)


def pct(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}%}"


# -----------------------------------------------------------------------------
# Sidebar navigation
# -----------------------------------------------------------------------------
st.sidebar.markdown("# ◈ RiskForge-QRM")
st.sidebar.caption("Interactive market-risk modelling & validation lab")
st.sidebar.markdown("---")
pages = {
    "⌂  Project Story": "Project Story",
    "◉  VaR Model Lab": "VaR Model Lab",
    "✓  Backtesting": "Backtesting",
    "⚡  Stress Testing": "Stress Testing",
    "↩  Reverse Stress": "Reverse Stress",
    "◌  Risk Attribution": "Risk Attribution",
    "i  Methodology": "Methodology",
}
page = pages[st.sidebar.radio("Navigate", list(pages.keys()), label_visibility="collapsed")]

st.sidebar.markdown("---")
st.sidebar.markdown("**Model setup**")
st.sidebar.markdown(
    f"<span class='rf-pill purple'>{confidence:.0%} confidence</span>"
    f"<span class='rf-pill purple'>{window}-day window</span>", unsafe_allow_html=True
)
st.sidebar.caption(f"EWMA λ = {ewma_lambda:.2f}  •  1-day horizon  •  {len(weights)} risk factors")
st.sidebar.markdown("**Risk factors**")
st.sidebar.caption(" · ".join(weights.keys()))
st.sidebar.markdown("---")
st.sidebar.caption("Educational prototype • presentation layer only")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown("<div class='rf-eyebrow'>Quantitative Market Risk • Model Validation</div>", unsafe_allow_html=True)
st.markdown(f"<div class='rf-title'>{page}</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. Project Story
# -----------------------------------------------------------------------------
if page == "Project Story":
    st.markdown(
        """<div class='rf-hero'>
        <h2>From market movements to a defensible risk decision.</h2>
        <p>RiskForge-QRM estimates one-day portfolio downside, checks whether the models behave reasonably, and then asks two practical questions: <b>what happens in a severe scenario?</b> and <b>which risk factors are responsible?</b></p>
        </div>""", unsafe_allow_html=True
    )

    # High-level result strip
    best = comparison.iloc[(comparison["exception_rate"] - comparison["target_rate"]).abs().argmin()]
    passed = int(stats["overall_pass"].sum()) if stats is not None else 0
    worst = None
    if stress is not None:
        ss = stress.groupby("scenario_id", as_index=False)["portfolio_loss"].first().sort_values("portfolio_loss", ascending=False)
        worst = ss.iloc[0]
    cols = st.columns(4)
    with cols[0]: metric_card("Closest VaR model", friendly_model(best.model_id), f"Exception rate {pct(best.exception_rate, 2)} vs {pct(best.target_rate, 0)} target")
    with cols[1]: metric_card("Validation result", f"{passed}/3 pass", "Coverage + independence checks")
    with cols[2]: metric_card("Worst configured stress", pct(float(worst.portfolio_loss), 2) if worst is not None else "—", str(worst.scenario_id) if worst is not None else "")
    with cols[3]: metric_card("Largest variance share", "75.1%", "Equity index in reference run")

    section("The project journey", "Each stage answers a simple question. This is the story to use in an interview.")
    steps = [
        ("01", "Build the portfolio", "Combine five market risk factors using fixed portfolio weights."),
        ("02", "Estimate VaR", "Compare historical, parametric and EWMA approaches at 99% confidence."),
        ("03", "Backtest the models", "Count exceptions and test whether their frequency and independence are reasonable."),
        ("04", "Stress the portfolio", "Apply severe but predefined factor shocks and measure portfolio loss."),
        ("05", "Reverse the question", "Find factor shocks that would be sufficient to reach a 10% loss target."),
        ("06", "Explain the risk", "Attribute portfolio variance and scenario losses back to individual factors."),
    ]
    cols = st.columns(3)
    for i, (num, title, copy) in enumerate(steps):
        with cols[i % 3]:
            st.markdown(
                f"<div class='rf-card rf-step'><div class='rf-step-num'>{num}</div><h3>{title}</h3><p>{copy}</p></div>",
                unsafe_allow_html=True,
            )

    section("The main finding", "The dashboard is not just a collection of charts; the outputs tell a consistent risk story.")
    st.markdown(
        f"<div class='rf-takeaway'><b>Reference run:</b> Parametric VaR is closest to the 1% target exception rate, while all three models pass the independence check. EWMA produces the highest exception rate and fails the unconditional coverage test. Under the configured stress scenarios, the equity-crash scenario is the most damaging at <b>{pct(float(worst.portfolio_loss),2) if worst is not None else '—'}</b>. Equity is also the dominant variance contributor.</div>",
        unsafe_allow_html=True,
    )

    section("What you should understand before opening the other pages")
    cols = st.columns(3)
    with cols[0]: card("VaR", "A threshold for how large a one-day loss could be at a chosen confidence level.", "rf-model")
    with cols[1]: card("Backtesting", "A reality check: compare the forecast with what actually happened.", "rf-model orange-top")
    with cols[2]: card("Stress testing", "A deliberate shock: ask how the portfolio behaves in an extreme scenario.", "rf-model cyan-top")

# -----------------------------------------------------------------------------
# 2. VaR Model Lab
# -----------------------------------------------------------------------------
elif page == "VaR Model Lab":
    section("Three ways to estimate the same risk question", "All three models estimate the 1-day downside threshold. Their main difference is how they describe the history of returns.")
    cards = [
        ("Historical VaR", "Let the observed return history speak for itself. No normal-distribution assumption.", "Empirical distribution", "rf-model"),
        ("Parametric VaR", "Summarise returns using mean and volatility, then use a distributional assumption.", "Distributional assumption", "rf-model orange-top"),
        ("EWMA VaR", "Give more weight to recent observations so volatility can react faster to changing conditions.", "Time-varying volatility", "rf-model cyan-top"),
    ]
    cols = st.columns(3)
    for i, (title, copy, tag, cls) in enumerate(cards):
        with cols[i]:
            st.markdown(f"<div class='rf-card {cls}'><h3>{title}</h3><p>{copy}</p><div class='small'><span class='rf-pill purple'>{tag}</span></div></div>", unsafe_allow_html=True)

    section("Model scoreboard", "The goal is not to find the fanciest model. It is to understand how each model behaves against realised losses.")
    c = comparison.copy()
    c["Model"] = c["model_id"].map(friendly_model)
    # Interactive dot plot: target vs observed exception rate.
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=c["exception_rate"] * 100, y=c["Model"], mode="markers+text", text=(c["exception_rate"]*100).map(lambda x: f"{x:.2f}%"),
        textposition="middle right", marker=dict(size=18, color="#8b7cff", line=dict(width=2, color="#ffffff")), name="Observed exception rate",
        hovertemplate="%{y}<br>Observed: %{x:.3f}%<extra></extra>"))
    fig.add_vline(x=float(c["target_rate"].iloc[0] * 100), line_dash="dash", line_color="#36d7d0", line_width=2, annotation_text="1% target", annotation_position="top")
    fig.update_xaxes(title="Exception rate (%)", range=[0.8, 1.8])
    fig.update_yaxes(title="", categoryorder="array", categoryarray=list(c["Model"])[::-1])
    chart(fig, 285)

    section("Explore one model", "Choose a model to see its VaR forecast against realised losses. The orange markers are exceptions.")
    selected = st.selectbox("Model", list(MODEL_NAMES), format_func=friendly_model, label_visibility="collapsed")
    bt = load_csv(f"backtest_{selected}")
    row = comparison[comparison.model_id == selected].iloc[0]
    if bt is not None:
        bt = bt.copy()
        bt["forecast_date"] = pd.to_datetime(bt["forecast_date"])
        # IMPORTANT: use bracket notation. bt.var is DataFrame.var (a method), not the CSV column.
        bt["var_pct"] = bt["var"] * 100
        bt["loss_pct"] = bt["realized_loss"] * 100
        ex = bt[bt["exception_flag"].astype(bool)]

        cols = st.columns(4)
        with cols[0]: metric_card("Exceptions", str(int(row.n_exceptions)), f"out of {int(row.n_forecasts)} forecasts")
        with cols[1]: metric_card("Exception rate", pct(row.exception_rate, 2), f"target {pct(row.target_rate, 0)}")
        with cols[2]: metric_card("Average VaR", pct(row.avg_var, 2), "average forecast threshold")
        with cols[3]: metric_card("Avg exceedance", pct(row.avg_exceedance_size, 2), "average size beyond VaR")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bt["forecast_date"], y=bt["loss_pct"], mode="lines", name="Realised loss", line=dict(color="#6f9cf8", width=1.2), hovertemplate="%{x|%d %b %Y}<br>Realised loss: %{y:.2f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=bt["forecast_date"], y=bt["var_pct"], mode="lines", name="VaR forecast", line=dict(color="#ff647c", width=2.2), hovertemplate="%{x|%d %b %Y}<br>VaR: %{y:.2f}%<extra></extra>"))
        fig.add_trace(go.Scatter(x=ex["forecast_date"], y=ex["loss_pct"], mode="markers", name="Exception", marker=dict(color="#ffb454", size=8, line=dict(color="#fff", width=1)), hovertemplate="%{x|%d %b %Y}<br>Exception: %{y:.2f}%<extra></extra>"))
        fig.update_layout(title=f"{friendly_model(selected)} — forecast vs realised portfolio loss", xaxis=dict(rangeslider=dict(visible=True), rangeselector=dict(buttons=[dict(count=1,label="1Y",step="year",stepmode="backward"),dict(count=3,label="3Y",step="year",stepmode="backward"),dict(step="all",label="All")])) )
        fig.update_yaxes(title="Loss / VaR (% of portfolio)")
        chart(fig, 520)
        st.markdown("<div class='rf-takeaway'><b>How to read it:</b> when realised loss rises above the red VaR line, the model has an exception. The project counts these exceptions and then statistically tests whether their frequency is reasonable.</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Backtesting
# -----------------------------------------------------------------------------
elif page == "Backtesting":
    section("A model is not finished when it produces a number", "Backtesting asks whether the model's forecasts behave consistently with what actually happened.")
    if stats is not None:
        cols = st.columns(3)
        for i, row in stats.iterrows():
            with cols[i]:
                status = bool(row["overall_pass"])
                cls = "green" if status else "red"
                label = "PASS" if status else "REVIEW"
                st.markdown(f"<div class='rf-card'><span class='rf-pill {cls}'>{label}</span><h3 style='margin-top:12px'>{friendly_model(row.model_id)}</h3><div class='rf-big'>{row.observed_rate:.2%}</div><p>observed exception rate</p><div class='small'>Kupiec p = {row.p_value:.4f} • Christoffersen p = {row.christ_p_value:.4f}</div></div>", unsafe_allow_html=True)

        section("Exception behaviour", "The 1% target is the line. A model close to it is not automatically 'best', but a large and statistically significant mismatch is a warning sign.")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=[friendly_model(x) for x in comparison.model_id], y=comparison.exception_rate*100, name="Observed", marker_color="#8b7cff", text=(comparison.exception_rate*100).map(lambda x:f"{x:.2f}%"), textposition="outside"))
        fig.add_hline(y=float(comparison.target_rate.iloc[0]*100), line_dash="dash", line_color="#36d7d0", line_width=2, annotation_text="1% target")
        fig.update_yaxes(title="Exception rate (%)", range=[0, 1.9])
        chart(fig, 340)

        section("What the tests mean", "These are standard, interview-friendly statistical checks — not black-box machine learning.")
        cols = st.columns(2)
        with cols[0]: card("Kupiec POF test", "Checks whether the number of exceptions is consistent with the target exception probability. Here the 5% significance level is used.", "rf-model")
        with cols[1]: card("Christoffersen independence", "Checks whether exceptions are clustered over time. Clustering can indicate that the model is slow to react to changing volatility.", "rf-model cyan-top")

        # Visual test matrix rather than a table.
        section("Validation verdict", "Green means the test did not provide enough evidence to reject the model's assumption at 5%.")
        for _, r in stats.iterrows():
            k_ok = not bool(r["reject_null_at_5pct"])
            ch_ok = not bool(r["christ_reject_null_at_5pct"])
            st.markdown(
                f"<div class='rf-card' style='margin-bottom:10px'><b>{friendly_model(r.model_id)}</b>"
                f"<span class='rf-pill {'green' if k_ok else 'red'}' style='float:right'>Kupiec {'PASS' if k_ok else 'REVIEW'}</span>"
                f"<span class='rf-pill {'green' if ch_ok else 'red'}' style='float:right'>Independence {'PASS' if ch_ok else 'REVIEW'}</span>"
                f"<p style='margin-top:10px'>Kupiec p-value: <b>{r.p_value:.4f}</b> • Christoffersen p-value: <b>{r.christ_p_value:.4f}</b></p></div>",
                unsafe_allow_html=True,
            )

        with st.expander("Show raw statistical test output"):
            st.dataframe(stats, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# 4. Stress testing
# -----------------------------------------------------------------------------
elif page == "Stress Testing":
    section("Move from 'typical day' to 'bad day'", "Stress testing deliberately imposes severe factor shocks. It answers a different question from VaR.")
    if stress is not None:
        ss = stress.groupby(["scenario_id", "description"], as_index=False)["portfolio_loss"].first().sort_values("portfolio_loss", ascending=False)
        worst = ss.iloc[0]
        cols = st.columns(3)
        with cols[0]: metric_card("Worst scenario", "Equity crash", "configured 2008-style scenario")
        with cols[1]: metric_card("Worst loss", pct(float(worst.portfolio_loss), 2), "portfolio-level result")
        with cols[2]: metric_card("Scenario count", str(len(ss)), "configured stress cases")

        section("Stress scenario leaderboard", "Longer bars mean larger portfolio losses under the configured scenario.")
        fig = go.Figure(go.Bar(
            x=ss["portfolio_loss"]*100, y=ss["scenario_id"], orientation="h",
            marker=dict(color=["#ff647c", "#ff8c75", "#ffb454", "#7c89a8"][:len(ss)]),
            text=(ss["portfolio_loss"]*100).map(lambda x:f"{x:.2f}%"), textposition="outside",
            hovertemplate="%{y}<br>Portfolio loss: %{x:.2f}%<extra></extra>"
        ))
        fig.update_layout(yaxis=dict(categoryorder="array", categoryarray=list(ss["scenario_id"])[::-1]), xaxis_title="Portfolio loss (%)")
        chart(fig, 370)

        section("What is driving each scenario?", "The heatmap shows the signed contribution of each risk factor. It is a visual version of the portfolio-weight calculation.")
        heat = stress.pivot_table(index="scenario_id", columns="risk_factor", values="factor_contribution", aggfunc="first").fillna(0)
        heat = heat.reindex(columns=list(weights.keys()))
        fig2 = go.Figure(go.Heatmap(z=heat.values*100, x=heat.columns, y=heat.index, colorscale=[[0,"#36d7d0"],[.5,"#10192c"],[1,"#ff647c"]], zmid=0, text=[[f"{v:.2f}%" for v in row] for row in heat.values*100], texttemplate="%{text}", hovertemplate="%{y}<br>%{x}<br>Contribution: %{z:.2f}%<extra></extra>"))
        fig2.update_xaxes(side="top")
        fig2.update_layout(title="Factor contribution by scenario", coloraxis_colorbar_title="Contribution")
        chart(fig2, 380)

        if sensitivity is not None:
            section("One-factor sensitivity: equity shock", "Hold the other factors unchanged and move the equity shock from +10% to -30%. This makes the portfolio's linear sensitivity easy to see.")
            fig3 = go.Figure(go.Scatter(x=sensitivity["shock"]*100, y=sensitivity["portfolio_loss"]*100, mode="lines+markers", line=dict(color="#36d7d0", width=3), marker=dict(size=8), fill="tozeroy", fillcolor="rgba(54,215,208,.08)"))
            fig3.add_hline(y=0, line_color="rgba(255,255,255,.25)")
            fig3.add_vline(x=-20, line_dash="dash", line_color="#ff647c", annotation_text="-20% equity shock")
            fig3.update_xaxes(title="Equity index shock (%)")
            fig3.update_yaxes(title="Portfolio loss (%)")
            chart(fig3, 360)

        with st.expander("Show scenario inputs and outputs"):
            st.dataframe(stress, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# 5. Reverse stress
# -----------------------------------------------------------------------------
elif page == "Reverse Stress":
    section("Start with the loss — then work backwards", "Instead of choosing a scenario first, the project asks what combination of factor shocks is sufficient to reach the chosen loss target.")
    if reverse is not None:
        solved = reverse.iloc[0]
        cols = st.columns(4)
        with cols[0]: metric_card("Target loss", pct(float(solved.target_loss), 0), "chosen adverse outcome")
        with cols[1]: metric_card("Solved loss", pct(float(solved.resulting_loss), 2), "loss produced by solution")
        with cols[2]: metric_card("Constraint", str(solved.constraint_status), "solution satisfies configured bounds")
        with cols[3]: metric_card("Solution size", f"{float(reverse_multi.l2_norm.iloc[0]):.3f}" if reverse_multi is not None else "—", "L2 norm of shock vector")

        rs = reverse.copy().sort_values("shock")
        fig = go.Figure(go.Bar(x=rs["shock"]*100, y=rs["risk_factor"], orientation="h", marker_color=["#ff647c" if x < 0 else "#36d7d0" for x in rs.shock], text=(rs["shock"]*100).map(lambda x:f"{x:.2f}%"), textposition="outside", hovertemplate="%{y}<br>Required shock: %{x:.2f}%<extra></extra>"))
        fig.add_vline(x=0, line_color="rgba(255,255,255,.35)")
        fig.update_xaxes(title="Required shock (%)")
        chart(fig, 380)

        st.markdown("<div class='rf-takeaway'><b>Plain-English interpretation:</b> the solver found a combination of shocks that produces a 10% portfolio loss while keeping the overall shock vector relatively small. Equity carries the largest required move in the reference solution.</div>", unsafe_allow_html=True)

        if reverse_multi is not None:
            section("Is the numerical solution stable?", "The same optimisation is started several times. Nearly identical results suggest the solution is not dependent on one lucky starting point.")
            fig2 = go.Figure(go.Scatter(x=reverse_multi["start"], y=reverse_multi["l2_norm"], mode="lines+markers", line=dict(color="#8b7cff", width=3), marker=dict(size=10), hovertemplate="Start %{x}<br>L2 norm: %{y:.6f}<extra></extra>"))
            fig2.add_hline(y=float(reverse_multi.l2_norm.mean()), line_dash="dash", line_color="#36d7d0", annotation_text="mean")
            fig2.update_xaxes(title="Optimisation start")
            fig2.update_yaxes(title="L2 norm")
            chart(fig2, 320)

        with st.expander("Show solved shock vector"):
            st.dataframe(reverse, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# 6. Attribution
# -----------------------------------------------------------------------------
elif page == "Risk Attribution":
    section("Turn one portfolio number into an explanation", "Risk attribution asks which factors are responsible for the portfolio's overall variability.")
    if vol is not None:
        v = vol.copy().sort_values("pct_of_portfolio_variance", ascending=False)
        top = v.iloc[0]
        cols = st.columns(3)
        with cols[0]: metric_card("Top driver", str(top.risk_factor), f"{top.pct_of_portfolio_variance:.1%} of variance")
        with cols[1]: metric_card("Portfolio weight", f"{top.weight:.0%}", "configured fixed weight")
        with cols[2]: metric_card("Second driver", "OIL", f"{v.iloc[1].pct_of_portfolio_variance:.1%} of variance")

        section("Variance contribution", "The sign matters: positive values add to portfolio variance, while negative values reduce it through diversification/covariance effects.")
        colors = ["#8b7cff" if x >= 0 else "#36d7d0" for x in v.pct_of_portfolio_variance]
        fig = go.Figure(go.Bar(x=v["pct_of_portfolio_variance"]*100, y=v["risk_factor"], orientation="h", marker_color=colors, text=(v["pct_of_portfolio_variance"]*100).map(lambda x:f"{x:.1f}%"), textposition="outside", hovertemplate="%{y}<br>Variance share: %{x:.2f}%<extra></extra>"))
        fig.add_vline(x=0, line_color="rgba(255,255,255,.35)")
        fig.update_xaxes(title="Share of portfolio variance (%)")
        chart(fig, 390)

        section("Stress contribution ranking", "A different question: across the configured stress scenarios, which factors tend to make the biggest absolute contribution?")
        if scenario_rank is not None:
            sr = scenario_rank.sort_values("avg_abs_contribution", ascending=True)
            fig2 = go.Figure(go.Bar(x=sr["avg_abs_contribution"]*100, y=sr["risk_factor"], orientation="h", marker_color="#ffb454", text=(sr["avg_abs_contribution"]*100).map(lambda x:f"{x:.2f}%"), textposition="outside", hovertemplate="%{y}<br>Average absolute contribution: %{x:.2f}%<extra></extra>"))
            fig2.update_xaxes(title="Average absolute scenario contribution (%)")
            chart(fig2, 350)

        with st.expander("Show attribution calculations"):
            st.dataframe(vol, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# 7. Methodology
# -----------------------------------------------------------------------------
elif page == "Methodology":
    section("The model choices behind the visuals", "Everything here is deliberately kept within standard statistics, probability and introductory quantitative-risk concepts.")
    cols = st.columns(4)
    with cols[0]: metric_card("Horizon", "1 day", "risk forecast horizon")
    with cols[1]: metric_card("Confidence", f"{confidence:.0%}", "VaR confidence level")
    with cols[2]: metric_card("Window", f"{window} days", "rolling estimation window")
    with cols[3]: metric_card("EWMA λ", f"{ewma_lambda:.2f}", "recent observations get more weight")

    section("Concept map", "These are the concepts you should be able to explain in an interview.")
    concepts = [
        ("Returns", "Convert price movements into percentage changes."),
        ("Volatility", "Measure how spread out returns are."),
        ("VaR", "Estimate a loss threshold at a chosen confidence level."),
        ("Expected Shortfall", "Look at the average loss beyond the VaR threshold."),
        ("Backtesting", "Compare forecasts with realised outcomes."),
        ("Stress testing", "Apply deliberately severe factor shocks."),
        ("Reverse stress", "Work backwards from a target loss."),
        ("Risk attribution", "Explain portfolio risk using factor contributions."),
    ]
    cols = st.columns(4)
    for i, (title, copy) in enumerate(concepts):
        with cols[i % 4]:
            st.markdown(f"<div class='rf-card' style='margin-bottom:12px'><h3>{title}</h3><p>{copy}</p></div>", unsafe_allow_html=True)

    section("Project assumptions", "The dashboard should make these visible because assumptions determine what the numbers mean.")
    cols = st.columns(2)
    with cols[0]:
        card("Portfolio", "Fixed weights across EQUITY_INDEX, RATES_10Y, FX_USD, OIL and GOLD. No rebalancing or transaction costs in the reference setup.")
    with cols[1]:
        card("Data & scope", "The reference run uses synthetic data. The project demonstrates modelling and validation workflow; it should not be presented as a real bank risk or regulatory capital calculation.", "rf-model orange-top")

    st.markdown("<div class='rf-takeaway'><b>Interview rule:</b> do not claim that the dashboard proves a model is 'correct'. Say that the backtests provide evidence about whether its observed behaviour is consistent with the chosen assumptions and significance level.</div>", unsafe_allow_html=True)

    report_path = RESULTS / "reports" / "model_validation_report.md"
    if report_path.exists():
        with st.expander("Open generated validation report"):
            st.markdown(report_path.read_text(encoding="utf-8"))

st.markdown("---")
st.caption("RiskForge-QRM • Educational market-risk prototype • Dashboard reads reproducible artefacts from results/")
