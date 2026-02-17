# Coastal Compound Flood Demo

## Overview

This project demonstrates a simple, transparent framework for understanding **compound coastal flood risk** using hourly water-level and hydrologic data.

Instead of focusing only on extreme peak water levels, the model emphasizes what actually drives real-world flooding impacts:

* persistence of high water
* failure of drainage windows
* multi-day accumulation of strain
* interaction between ocean, rainfall, and river inputs

The goal is **public literacy and conceptual clarity**, not forecasting.

It shows how compound coastal risk emerges when water cannot fully recede between tidal cycles.

---

## Core Idea

Coastal flooding rarely comes from a single extreme surge.

It usually results from **compound processes** acting together:

* Sea-level rise raising the baseline
* Tides and storm surge adding short-term peaks
* River discharge blocking outflow
* Rainfall or saturated soils preventing drainage

The most dangerous condition is **persistent high water** across multiple days, when systems cannot recover between cycles.

This demo models that dynamic using simple, interpretable metrics.

---

## Metrics Computed from Hourly Data

Given a CSV of hourly observations, the app computes daily flood-strain indicators.

All hourly excess values are expressed in **meter-hours (m·hr)**.

---

### 1. Effective Water Level (EWL)

A proxy for total coastal water level combining ocean forcing and baseline shifts.

```
EWL = water_level_m + slr_adjust_m + wave_setup_m
```

Where:

* `water_level_m` = observed tide/surge height
* `slr_adjust_m` = mean sea-level rise offset (optional)
* `wave_setup_m` = additional wave setup contribution (optional)

If optional columns are missing, they default to zero.

---

### 2. Cumulative Flood Load (CFL)

Measures how much flood strain builds during high-water periods.

```
baseline = nuisance flood threshold
CFL_hour = max(EWL - baseline, 0)
daily_CFL = sum(CFL_hour)
cumulative_CFL = running sum
```

The baseline typically represents:

* Mean Higher High Water (MHHW), or
* A local nuisance flooding level (often 0.5–1.0 m above normal tide)

CFL represents **flood volume exposure over time**, not just peak height.

---

### 3. Persistent High-Water Excess (PHWe)

Captures failure of drainage during low-water windows.

This is the most critical indicator of compound flood risk.

```
baseline_drainage = drainage threshold
PHWe_hour = max(EWL - baseline_drainage, 0)
daily_PHWe = sum over low-drainage window
cumulative_PHWe = running sum
```

The low-drainage window is approximated as **20:00–08:00**, representing periods when water should normally recede.

PHWe measures how long systems remain unable to drain.

---

### 4. Compound Flood Strain

A compound cycle occurs when:

```
high_water_day = daily_CFL > threshold_CFL
poor_drainage_night = daily_PHWe > threshold_PHWe
compound = high_water_day AND poor_drainage_night
```

The model tracks streaks of:

* consecutive high-water days
* consecutive drainage failures
* consecutive compound cycles

These streaks represent **system fatigue**.

---

## Risk States (Daily Operational Classification)

Risk is evaluated **per day**, based on current strain and persistence — not long-term rarity.

```
Stable:
  low daily_CFL
  low daily_PHWe
  short or no streaks

Straining:
  moderate daily accumulation
  or multiple consecutive compound cycles

Failure:
  high daily excess
  or prolonged compound streaks
```

This reflects how real flooding impacts emerge: from sustained inability to recover between tidal cycles.

---

## Nonlinear Escalation Gauge

The model includes a simple multiplier illustrating how risk accelerates as strain compounds.

```
risk_multiplier =
  1
  + (daily_CFL / norm_CFL)
  + (daily_PHWe / norm_PHWe)
  + (compound_streak * factor)
```

This captures the reality that flood damage increases **nonlinearly** once persistence and compounding begin.

---

## Visualizations

The app generates five panels:

### Timeline

Water level and effective water level over time with baseline reference.

### CFL Curve

Accumulated flood load across days.

### PHWe Bars

Daily drainage failure intensity.

### Risk State Band

Color-coded operational risk:

* Green = Stable
* Amber = Straining
* Red = Failure

### Nonlinear Escalation Gauge

Shows how compound strain accelerates risk.

Outputs are saved as **PNG and interactive HTML** in `/output`.

---

## Input CSV Format

Required columns:

```
timestamp (ISO8601)
water_level_m (float)
discharge_m3s (float)
rainfall_mm (float)
```

Optional columns:

```
slr_adjust_m
wave_setup_m
soil_moisture
```

---

## Why This Matters

Sea-level rise does more than increase peak flood heights.

It changes the system in deeper ways:

* Rare floods become routine
* Drainage windows shrink
* Tidal cycles overlap
* Rainfall and rivers can no longer discharge efficiently

The greatest risk is not the highest surge.

It is **persistent high water with no recovery between cycles**.

This demo illustrates how simple accumulation metrics can reveal that danger early.

---

## How to Run

Install dependencies:

```
pip install -r requirements.txt
```

Run the demo:

```
python src/main.py
```

To use your own data:

```
python src/main.py data/your_file.csv
```

Your CSV must follow the input schema above.

---

## Purpose

This is not a forecasting or engineering model.

It is a **conceptual and public-literacy tool** designed to help users understand compound coastal flood dynamics and the role of persistence in real-world risk.

---

## License

MIT License — free to use, modify, and build upon.
