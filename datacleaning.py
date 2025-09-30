"""
NYC Yellow Taxi cleaning with pandas per Docs/cleaning_rules.md.

Reads: NYC_YELLOW_TAXI_RAW.csv, Docs/taxi_zone_lookup.csv
Writes: NYC_YELLOW_TAXI_CLEAN.csv, Docs/cleaning_report.md
"""

from __future__ import annotations

import os
from typing import Iterable
import pandas as pd


WORKSPACE_ROOT = "/Users/harish/FDM_EDA"
RAW_CSV = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_RAW.csv")
ZONES_CSV = os.path.join(WORKSPACE_ROOT, "Docs", "taxi_zone_lookup.csv")
CLEAN_CSV = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_CLEAN.csv")
REPORT_MD = os.path.join(WORKSPACE_ROOT, "Docs", "cleaning_report.md")


def _read_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(
        RAW_CSV,
        dtype={
            # Allow pandas to infer floats for amounts; IDs cast later
            "VendorID": "Int64",
            "PULocationID": "Int64",
            "DOLocationID": "Int64",
            "payment_type": "Int64",
            "RatecodeID": "Float64",
            "passenger_count": "Float64",
        },
        parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
        keep_default_na=True,
    )
    zones = pd.read_csv(ZONES_CSV)
    zones.columns = [c.strip() for c in zones.columns]
    return df, zones


def _log(report: list[str], line: str) -> None:
    report.append(line)


def _coalesce_sum(values: Iterable[pd.Series]) -> pd.Series:
    result = None
    for s in values:
        if result is None:
            result = s
        else:
            result = result.add(s.fillna(0), fill_value=0)
    assert result is not None
    return result


def clean() -> None:
    report: list[str] = []

    df, zones = _read_inputs()
    _log(report, f"Loaded raw rows: {len(df):,}")

    # 1) Column types and normalization
    for col in [
        "fare_amount",
        "extra",
        "mta_tax",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "total_amount",
        "congestion_surcharge",
        "airport_fee",
        "trip_distance",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Float64")

    if "store_and_fwd_flag" in df.columns:
        df["store_and_fwd_flag"] = df["store_and_fwd_flag"].astype("string").str.upper()
        df.loc[~df["store_and_fwd_flag"].isin(["Y", "N"]), "store_and_fwd_flag"] = pd.NA

    # 2) Valid domains
    before = len(df)
    df = df[df["VendorID"].isin([1, 2]) | df["VendorID"].isna()]
    _log(report, f"Dropped invalid VendorID rows: {before - len(df):,}")

    # Ratecode: keep nulls, set invalid to null
    df["RatecodeID"] = df["RatecodeID"].astype("Float64")
    df.loc[~df["RatecodeID"].isin([1, 2, 3, 4, 5, 6]) & df["RatecodeID"].notna(), "RatecodeID"] = pd.NA
    df["RatecodeID"] = df["RatecodeID"].astype("Int64")

    # payment_type: 0 -> NA
    df.loc[df["payment_type"].eq(0), "payment_type"] = pd.NA

    # 3) Datetime sanity
    before = len(df)
    bad_order = df["tpep_dropoff_datetime"] < df["tpep_pickup_datetime"]
    df = df[~bad_order]
    _log(report, f"Dropped dropoff<pickup: {before - len(df):,}")

    df["trip_duration_min"] = (
        (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60.0
    )

    before = len(df)
    df = df[df["trip_duration_min"] <= 24 * 60]
    _log(report, f"Dropped >24h duration: {before - len(df):,}")

    before = len(df)
    zero_minute = df["trip_duration_min"].fillna(0).round(5).eq(0)
    df = df[~(zero_minute & df["trip_distance"].fillna(0).round(5).eq(0))]
    _log(report, f"Dropped zero-minute with zero-distance: {before - len(df):,}")

    # 4) Distance sanity
    before = len(df)
    df = df[df["trip_distance"].isna() | (df["trip_distance"] >= 0)]
    _log(report, f"Dropped negative distance: {before - len(df):,}")

    before = len(df)
    df = df[df["trip_distance"].isna() | (df["trip_distance"] <= 200)]
    _log(report, f"Dropped extreme distance >200mi: {before - len(df):,}")

    # 5) Monetary fields and totals
    # Set negative component fees to null
    for col in [
        "extra",
        "mta_tax",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "congestion_surcharge",
        "airport_fee",
    ]:
        neg_mask = df[col] < 0
        nneg = int(neg_mask.sum())
        df.loc[neg_mask, col] = pd.NA
        if nneg:
            _log(report, f"Set negatives to NA for {col}: {nneg:,}")

    # For non-dispute/voided, drop negative fare/total
    non_adj = (~df["payment_type"].isin([4, 6])).fillna(False)
    before = len(df)
    df = df[(df["fare_amount"].isna() | (df["fare_amount"] >= 0)) | ~non_adj]
    dropped = before - len(df)
    if dropped:
        _log(report, f"Dropped negative fare for non-adjustment payments: {dropped:,}")

    before = len(df)
    # Recompute mask after potential row drops to keep index aligned
    non_adj = (~df["payment_type"].isin([4, 6])).fillna(False)
    df = df[(df["total_amount"].isna() | (df["total_amount"] >= 0)) | ~non_adj]
    dropped = before - len(df)
    if dropped:
        _log(report, f"Dropped negative total for non-adjustment payments: {dropped:,}")

    # Recompute total and replace when mismatch > 0.01
    computed_total = _coalesce_sum(
        [
            df["fare_amount"],
            df["extra"],
            df["mta_tax"],
            df["tip_amount"],
            df["tolls_amount"],
            df["improvement_surcharge"],
            df["congestion_surcharge"],
            df["airport_fee"],
        ]
    )
    mismatch = (df["total_amount"] - computed_total).abs() > 0.01
    nmismatch = int(mismatch.fillna(False).sum())
    df.loc[mismatch, "total_amount"] = computed_total[mismatch]
    _log(report, f"Replaced mismatched total_amount: {nmismatch:,}")

    # 6) Passenger count capping
    df["passenger_count"] = pd.to_numeric(df["passenger_count"], errors="coerce")
    df.loc[df["passenger_count"] < 0, "passenger_count"] = pd.NA
    df.loc[df["passenger_count"] > 6, "passenger_count"] = pd.NA
    df["passenger_count"] = df["passenger_count"].astype("Int64")

    # 7) Deduplicate
    subset = [
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "PULocationID",
        "DOLocationID",
        "trip_distance",
        "fare_amount",
        "payment_type",
    ]
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first")
    _log(report, f"Dropped exact duplicates: {before - len(df):,}")

    # 8) Zone mapping
    zones = zones.rename(columns={
        "LocationID": "LocationID",
        "Borough": "Borough",
        "Zone": "Zone",
        "service_zone": "service_zone",
    })

    pu = zones.add_prefix("PU_")
    pu = pu.rename(columns={"PU_LocationID": "PULocationID"})
    do = zones.add_prefix("DO_")
    do = do.rename(columns={"DO_LocationID": "DOLocationID"})

    df = df.merge(pu[["PULocationID", "PU_Borough", "PU_Zone", "PU_service_zone"]], on="PULocationID", how="left")
    df = df.merge(do[["DOLocationID", "DO_Borough", "DO_Zone", "DO_service_zone"]], on="DOLocationID", how="left")

    # Drop rows with unmapped zones to ensure names are present in final dataset
    before = len(df)
    unmapped = df["PU_Zone"].isna() | df["DO_Zone"].isna()
    df = df[~unmapped]
    _log(report, f"Dropped rows with unmapped PU/DO zones: {before - len(df):,}")

    # 9) Final types
    for col in ["VendorID", "PULocationID", "DOLocationID", "payment_type"]:
        df[col] = df[col].astype("Int64")

    # RatecodeID already Int64; ensure float numeric columns are Float64
    for col in [
        "fare_amount",
        "extra",
        "mta_tax",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "total_amount",
        "congestion_surcharge",
        "airport_fee",
        "trip_distance",
        "trip_duration_min",
    ]:
        df[col] = df[col].astype("Float64")

    # 10) Output
    df.to_csv(CLEAN_CSV, index=False)

    # Report summary
    os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        for line in report:
            f.write(line + "\n")
        f.write(f"Final rows: {len(df):,}\n")


if __name__ == "__main__":
    clean()


