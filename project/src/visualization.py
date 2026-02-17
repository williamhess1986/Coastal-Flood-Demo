from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go


STATE_COLOR = {
    "Stable": "green",
    "Straining": "orange",
    "Failure": "red",
}


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def plot_timeline(hourly: pd.DataFrame, daily: pd.DataFrame, outdir: Path) -> Path:
    _ensure_dir(outdir)
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=daily.index, y=daily["max_ewl_m"], mode="lines+markers", name="Daily max EWL (m)")) 
    fig.add_trace(go.Scatter(x=daily.index, y=daily["min_ewl_m"], mode="lines+markers", name="Daily min EWL (m)"))

    fig.add_trace(go.Bar(x=daily.index, y=daily["sum_rainfall_mm"], name="Daily rainfall (mm)", yaxis="y2", opacity=0.5))

    fig.update_layout(
        title="Panel 1 — Water level timeline (daily max/min) + rainfall",
        xaxis_title="Date (UTC)",
        yaxis=dict(title="EWL (m)"),
        yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right"),
        legend=dict(orientation="h"),
        height=500,
    )

    outpath = outdir / "panel1_timeline.html"
    fig.write_html(str(outpath), include_plotlyjs="cdn")
    return outpath


def plot_cfl_curve(daily: pd.DataFrame, outdir: Path) -> Path:
    _ensure_dir(outdir)
    plt.figure()
    plt.plot(daily.index, daily["cumulative_CFL"])
    plt.title("Panel 2 — Cumulative Flood Load (CFL)")
    plt.xlabel("Date (UTC)")
    plt.ylabel("Cumulative CFL (m·h)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    outpath = outdir / "panel2_cfl_curve.png"
    plt.savefig(outpath, dpi=180)
    plt.close()
    return outpath


def plot_phwe_bars(daily: pd.DataFrame, outdir: Path) -> Path:
    _ensure_dir(outdir)
    plt.figure()
    plt.bar(daily.index, daily["daily_PHWe"])
    plt.title("Panel 3 — Persistent High-Water Excess (PHWe) during night window")
    plt.xlabel("Date (UTC)")
    plt.ylabel("Daily PHWe (m·h)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    outpath = outdir / "panel3_phwe_bars.png"
    plt.savefig(outpath, dpi=180)
    plt.close()
    return outpath


def plot_risk_band(daily: pd.DataFrame, outdir: Path) -> Path:
    _ensure_dir(outdir)
    colors = [STATE_COLOR.get(s, "gray") for s in daily["risk_state"].astype(str).tolist()]

    fig = go.Figure(go.Bar(
        x=daily.index,
        y=[1] * len(daily),
        marker_color=colors,
        showlegend=False,
        hovertext=daily["risk_state"],
    ))
    fig.update_layout(
        title="Panel 4 — Daily risk state",
        xaxis_title="Date (UTC)",
        yaxis=dict(title="", showticklabels=False, range=[0, 1.2]),
        height=250,
    )

    outpath = outdir / "panel4_risk_band.html"
    fig.write_html(str(outpath), include_plotlyjs="cdn")
    return outpath


def plot_escalation_gauge(daily: pd.DataFrame, outdir: Path) -> Path:
    _ensure_dir(outdir)
    plt.figure()
    plt.plot(daily.index, daily["risk_multiplier"])
    plt.title("Panel 5 — Nonlinear escalation gauge (risk_multiplier)")
    plt.xlabel("Date (UTC)")
    plt.ylabel("risk_multiplier (dimensionless)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    outpath = outdir / "panel5_escalation_gauge.png"
    plt.savefig(outpath, dpi=180)
    plt.close()
    return outpath


def generate_all_plots(hourly: pd.DataFrame, daily: pd.DataFrame, outdir: Path) -> dict[str, Path]:
    outputs = {}
    outputs["panel1_timeline"] = plot_timeline(hourly, daily, outdir)
    outputs["panel2_cfl_curve"] = plot_cfl_curve(daily, outdir)
    outputs["panel3_phwe_bars"] = plot_phwe_bars(daily, outdir)
    outputs["panel4_risk_band"] = plot_risk_band(daily, outdir)
    outputs["panel5_escalation_gauge"] = plot_escalation_gauge(daily, outdir)
    return outputs
