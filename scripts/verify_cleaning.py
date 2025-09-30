"""
Verify that NYC_YELLOW_TAXI_CLEAN.csv satisfies Docs/cleaning_rules.md constraints.

Writes: Docs/verification_report.md with pass/fail counts.
"""

import os
import pandas as pd


WORKSPACE_ROOT = "/Users/harish/FDM_EDA"
CLEAN_CSV = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_CLEAN.csv")
REPORT_MD = os.path.join(WORKSPACE_ROOT, "Docs", "verification_report.md")


def main() -> None:
    df = pd.read_csv(CLEAN_CSV, parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"])

    checks = {}

    checks["vendor_valid"] = df["VendorID"].isin([1, 2]).all()
    checks["ratecode_valid"] = df["RatecodeID"].isna() | df["RatecodeID"].isin([1, 2, 3, 4, 5, 6])
    checks["ratecode_valid"] = bool(checks["ratecode_valid"].all())

    checks["payment_valid"] = df["payment_type"].isna() | df["payment_type"].isin([1, 2, 3, 4, 5, 6])
    checks["payment_valid"] = bool(checks["payment_valid"].all())

    checks["saf_valid"] = df["store_and_fwd_flag"].isna() | df["store_and_fwd_flag"].isin(["Y", "N"])
    checks["saf_valid"] = bool(checks["saf_valid"].all())

    checks["distance_range"] = bool(((df["trip_distance"] >= 0) & (df["trip_distance"] <= 200)).all())

    checks["drop_ge_pick"] = bool((df["tpep_dropoff_datetime"] >= df["tpep_pickup_datetime"]).all())
    checks["dur_le_24h"] = bool((df["trip_duration_min"] <= 24 * 60).all())
    zero_minute = df["trip_duration_min"].round(5).eq(0)
    checks["zero_min_distance_positive"] = bool((~zero_minute | df["trip_distance"].round(5).gt(0)).all())

    non_adj = ~df["payment_type"].isin([4, 6]).fillna(False)
    checks["fare_nonneg_when_not_adjust"] = bool((df.loc[non_adj, "fare_amount"] >= 0).all())
    checks["total_nonneg_when_not_adjust"] = bool((df.loc[non_adj, "total_amount"] >= 0).all())

    # Recompute total and compare
    comp = (
        df["fare_amount"].fillna(0)
        + df["extra"].fillna(0)
        + df["mta_tax"].fillna(0)
        + df["tip_amount"].fillna(0)
        + df["tolls_amount"].fillna(0)
        + df["improvement_surcharge"].fillna(0)
        + df["congestion_surcharge"].fillna(0)
        + df["airport_fee"].fillna(0)
    )
    checks["total_matches_components"] = bool((df["total_amount"].fillna(0) - comp).abs().le(0.01).all())

    checks["pu_zone_present"] = bool(df["PU_Zone"].notna().all())
    checks["do_zone_present"] = bool(df["DO_Zone"].notna().all())

    os.makedirs(os.path.join(WORKSPACE_ROOT, "Docs"), exist_ok=True)
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("# Cleaning verification\n\n")
        f.write(f"Total rows: {len(df):,}\n\n")
        for name, ok in checks.items():
            f.write(f"- {name}: {'PASS' if ok else 'FAIL'}\n")


if __name__ == "__main__":
    main()


