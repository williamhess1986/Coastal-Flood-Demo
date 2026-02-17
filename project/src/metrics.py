from __future__ import annotations

import pandas as pd


def compute_effective_water_level(hourly: pd.DataFrame) -> pd.Series:
    """Effective Water Level (EWL): tide/surge proxy + mean SLR + optional wave setup."""
    ewl = hourly["water_level_m"] + hourly.get("slr_adjust_m", 0.0) + hourly.get("wave_setup_m", 0.0)
    return ewl.rename("ewl_m")


def compute_daily_metrics(
    hourly: pd.DataFrame,
    baseline_day_m: float = 1.0,
    baseline_night_m: float = 0.7,
    night_start_hour: int = 20,
    night_end_hour: int = 8,
) -> pd.DataFrame:
    """Compute daily compound flooding metrics from hourly data."""
    df = hourly.copy()
    df["ewl_m"] = compute_effective_water_level(df)

    df["cfl_hour"] = (df["ewl_m"] - baseline_day_m).clip(lower=0)

    hours = df.index.hour
    is_night = (hours >= night_start_hour) | (hours < night_end_hour)
    df["phwe_hour"] = 0.0
    df.loc[is_night, "phwe_hour"] = (df.loc[is_night, "ewl_m"] - baseline_night_m).clip(lower=0)

    daily = pd.DataFrame(index=df.resample("1D").sum(numeric_only=True).index)
    daily["daily_CFL"] = df["cfl_hour"].resample("1D").sum()
    daily["daily_PHWe"] = df["phwe_hour"].resample("1D").sum()

    daily["max_ewl_m"] = df["ewl_m"].resample("1D").max()
    daily["min_ewl_m"] = df["ewl_m"].resample("1D").min()
    daily["mean_rainfall_mm"] = df["rainfall_mm"].resample("1D").mean()
    daily["sum_rainfall_mm"] = df["rainfall_mm"].resample("1D").sum()
    daily["mean_discharge_m3s"] = df["discharge_m3s"].resample("1D").mean()

    daily["cumulative_CFL"] = daily["daily_CFL"].cumsum()
    daily["cumulative_PHWe"] = daily["daily_PHWe"].cumsum()

    severe_baseline_night_m = 1.0
    df["severe_phwe_hour"] = 0.0
    df.loc[is_night, "severe_phwe_hour"] = (df.loc[is_night, "ewl_m"] - severe_baseline_night_m).clip(lower=0)
    daily["daily_severe_PHWe"] = df["severe_phwe_hour"].resample("1D").sum()
    daily["cumulative_severe_PHWe"] = daily["daily_severe_PHWe"].cumsum()

    return daily
