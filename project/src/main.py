from __future__ import annotations

from pathlib import Path
import sys

# Allow running as: python src/main.py ...
# (This project intentionally avoids requiring src/ to be a Python package with __init__.py.)
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_loader import load_hourly_csv
from metrics import compute_daily_metrics
from risk_states import assign_risk_state, compute_risk_multiplier
from visualization import generate_all_plots


def _summary_table(daily):
    summary = daily.copy()
    summary["date"] = summary.index.date
    cols = [
        "date",
        "daily_CFL",
        "daily_PHWe",
        "cumulative_CFL",
        "cumulative_PHWe",
        "consecutive_compound_cycles",
        "risk_multiplier",
        "risk_state",
    ]
    return summary[cols].tail(14)


def run(path: str) -> None:
    project_root = SRC_DIR.parent  # .../project
    outdir = project_root / "output"
    outdir.mkdir(parents=True, exist_ok=True)

    loaded = load_hourly_csv(path)
    hourly = loaded.hourly

    daily = compute_daily_metrics(hourly)
    daily = assign_risk_state(daily)
    daily["risk_multiplier"] = compute_risk_multiplier(daily)

    daily_out = outdir / f"daily_metrics_{Path(path).stem}.csv"
    daily.reset_index(names="date_utc").to_csv(daily_out, index=False)

    plot_paths = generate_all_plots(hourly, daily, outdir)

    print("\n=== Coastal Compound Flood Demo — Summary (last 14 days) ===")
    print(_summary_table(daily).to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
    print(f"\nSaved daily metrics to: {daily_out}")
    print("Saved plots:")
    for k, v in plot_paths.items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python src/main.py data/<your_file.csv>\n\n"
            "Example: python src/main.py data/sample_chicago_1995.csv"
        )
        raise SystemExit(2)

    run(sys.argv[1])
