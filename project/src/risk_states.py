from __future__ import annotations

import pandas as pd

HOT_DAY_CFL = 6.0
HOT_NIGHT_PHWE = 3.0

STABLE_MAX_CFL = 40.0
STABLE_MAX_PHWE = 20.0
STABLE_MAX_COMPOUND_STREAK = 1

STRAINING_MIN_CFL = 40.0
STRAINING_MIN_PHWE = 20.0
STRAINING_MIN_COMPOUND_STREAK = 2

FAILURE_MIN_CFL = 80.0
FAILURE_MIN_PHWE = 40.0
FAILURE_MIN_COMPOUND_STREAK = 4


def _streak(series_bool: pd.Series) -> pd.Series:
    streak = []
    current = 0
    for v in series_bool.fillna(False).astype(bool).tolist():
        if v:
            current += 1
        else:
            current = 0
        streak.append(current)
    return pd.Series(streak, index=series_bool.index)


def compute_compound_streaks(daily: pd.DataFrame) -> pd.DataFrame:
    out = daily.copy()
    out["hot_day"] = out["daily_CFL"] > HOT_DAY_CFL
    out["hot_night"] = out["daily_PHWe"] > HOT_NIGHT_PHWE
    out["compound"] = out["hot_day"] & out["hot_night"]

    out["consecutive_hot_days"] = _streak(out["hot_day"])
    out["consecutive_hot_nights"] = _streak(out["hot_night"])
    out["consecutive_compound_cycles"] = _streak(out["compound"])
    return out


def assign_risk_state(daily: pd.DataFrame) -> pd.DataFrame:
    out = compute_compound_streaks(daily)

    cfl = out["cumulative_CFL"]
    phwe = out["cumulative_PHWe"]
    streak = out["consecutive_compound_cycles"]

    state = pd.Series(["Stable"] * len(out), index=out.index, dtype="object")

    failure = (cfl >= FAILURE_MIN_CFL) | (phwe >= FAILURE_MIN_PHWE) | (streak >= FAILURE_MIN_COMPOUND_STREAK)
    state.loc[failure] = "Failure"

    straining = (cfl >= STRAINING_MIN_CFL) | (phwe >= STRAINING_MIN_PHWE) | (streak >= STRAINING_MIN_COMPOUND_STREAK)
    state.loc[straining & ~failure] = "Straining"

    out["risk_state"] = state
    return out


def compute_risk_multiplier(
    daily: pd.DataFrame,
    norm_cfl: float = 40.0,
    norm_phwe: float = 20.0,
    streak_factor: float = 0.5,
) -> pd.Series:
    rm = 1 + (daily["cumulative_CFL"] / norm_cfl) + (daily["cumulative_PHWe"] / norm_phwe) + (daily["consecutive_compound_cycles"] * streak_factor)
    return rm.rename("risk_multiplier")
