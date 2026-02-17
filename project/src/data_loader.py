from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"timestamp", "water_level_m", "discharge_m3s", "rainfall_mm"}
OPTIONAL_COLUMNS = {"soil_moisture", "slr_adjust_m", "wave_setup_m"}


@dataclass(frozen=True)
class LoadResult:
    hourly: pd.DataFrame
    source_path: Path


def load_hourly_csv(path: str | Path) -> LoadResult:
    """Load a coastal compound flooding CSV and validate schema.

    Required columns:
      - timestamp (ISO8601)
      - water_level_m (float): observed / modeled water level above local datum (tide + surge proxy)
      - discharge_m3s (float): river discharge proxy
      - rainfall_mm (float): local rainfall proxy

    Optional:
      - soil_moisture (0–1): catchment wetness proxy
      - slr_adjust_m (float): additive mean sea-level rise adjustment
      - wave_setup_m (float): additive wave setup adjustment
    """
    p = Path(path)
    df = pd.read_csv(p)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}. Found: {sorted(df.columns)}"
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="raise")
    df = df.sort_values("timestamp").set_index("timestamp")

    for col in REQUIRED_COLUMNS - {"timestamp"}:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in OPTIONAL_COLUMNS & set(df.columns):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df.index.duplicated().any():
        df = df[~df.index.duplicated(keep="first")]

    keep = list(REQUIRED_COLUMNS - {"timestamp"}) + sorted(list(OPTIONAL_COLUMNS & set(df.columns)))
    df = df[keep]

    for adj in ["slr_adjust_m", "wave_setup_m"]:
        if adj not in df.columns:
            df[adj] = 0.0
        else:
            df[adj] = df[adj].fillna(0.0)

    if "soil_moisture" in df.columns:
        df["soil_moisture"] = df["soil_moisture"].clip(lower=0, upper=1)

    for col in ["water_level_m", "discharge_m3s", "rainfall_mm"]:
        if df[col].isna().all():
            raise ValueError(f"Column '{col}' is all-NaN after parsing.")

    return LoadResult(hourly=df, source_path=p)
