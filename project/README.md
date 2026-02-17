# Coastal Compound Flood Demo App

**Beyond peak water level: recovery windows and system margins matter more.**

This demo project computes and visualizes **compound flooding risk** from hourly coastal water-level time series,
optionally combined with river discharge and rainfall. The key idea is that the biggest impacts often come from
**multi-day persistence of high water** (no drainage/recovery) plus upstream or pluvial inputs that block outflow.

## What it measures

### 1) Effective Water Level (EWL)

A simple proxy for total coastal water level:

```
EWL = water_level_m + slr_adjust_m + wave_setup_m
```

- `water_level_m` is your tide+surge proxy (observed gauge or model output).
- `slr_adjust_m` is an optional additive mean sea-level rise adjustment.
- `wave_setup_m` is an optional additive wave setup term.

### 2) Cumulative Flood Load (CFL)

**CFL** represents all-hours exposure above a nuisance threshold (e.g., when roads, pumps, or outfalls start to struggle):

```
baseline_day_m = 1.0
CFL_hour = max(EWL - baseline_day_m, 0)
daily_CFL = sum(CFL_hour)
cumulative_CFL = running sum
```

Units are **meter-hours (m·h)** because we sum hourly exceedance.

### 3) Persistent High-Water Excess (PHWe)

**PHWe** captures “no recovery” nights, when water fails to recede below a drainage threshold:

Night window (proxy): **20:00–08:00 UTC**

```
baseline_night_m = 0.7
PHWe_hour = max(EWL - baseline_night_m, 0)  (only during night window)
daily_PHWe = sum(PHWe_hour)
cumulative_PHWe = running sum
```

A **severe** diagnostic variant is also computed using a higher drainage threshold.

### 4) Compound Day–Night Strain + Streaks

A “compound cycle” occurs when a **high-load day** and a **poor-drainage night** happen back-to-back:

- `hot_day = daily_CFL > 6.0`
- `hot_night = daily_PHWe > 3.0`
- `compound = hot_day AND hot_night`

The app tracks:

- `consecutive_hot_days`
- `consecutive_hot_nights`
- `consecutive_compound_cycles`

### 5) Risk States

The app assigns a **daily risk_state**:

- **Stable**: `cumulative_CFL < 40` AND `cumulative_PHWe < 20` AND `compound_streak < 2`
- **Straining**: `cumulative_CFL >= 40` OR `cumulative_PHWe >= 20` OR `compound_streak >= 2`
- **Failure**: `cumulative_CFL >= 80` OR `cumulative_PHWe >= 40` OR `compound_streak >= 4`

> These thresholds are tuned for the included synthetic demo data. For real sites, calibrate to local datums,
> nuisance thresholds (e.g., MHHW-based), and infrastructure tolerances.

### 6) Nonlinear Escalation Gauge

A simple “how fast things are getting worse” index:

```
risk_multiplier = 1 + (cumulative_CFL/40) + (cumulative_PHWe/20) + (compound_streak * 0.5)
```

This captures how exposure often grows **nonlinearly** as sea level rises and recovery windows disappear.

## Visual outputs

The app generates five panels in `output/`:

1. Timeline: daily max/min EWL + rainfall overlay (HTML, Plotly)
2. Cumulative CFL curve (PNG)
3. PHWe bars (PNG)
4. Risk state band (HTML, Plotly)
5. Nonlinear escalation gauge (PNG)

## Install & run

### 1) Install dependencies

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Run on a sample dataset

```bash
python src/main.py data/sample_chicago_1995.csv
```

(Yes, the filenames are inherited from the heat-load template; the *contents* are coastal flooding samples.)

Outputs are written to:

- `output/daily_metrics_<dataset>.csv`
- `output/panel*.png` and `output/panel*.html`

## Use your own CSV

Create an hourly CSV with **required columns**:

- `timestamp` (ISO8601)
- `water_level_m` (float)
- `discharge_m3s` (float)
- `rainfall_mm` (float)

Optional:

- `soil_moisture` (0–1)
- `slr_adjust_m` (float)
- `wave_setup_m` (float)

Then run:

```bash
python src/main.py data/your_file.csv
```

## Notebook

A quick-start notebook is in `notebooks/demo.ipynb`.
