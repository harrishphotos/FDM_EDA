import os
import pandas as pd

WORKSPACE_ROOT = "/Users/harish/FDM_EDA"
CLEAN_CSV = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_CLEAN.csv")
CLEAN_PARQUET = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_CLEAN.parquet")


def main() -> None:
    df = pd.read_csv(
        CLEAN_CSV,
        parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
    )
    df.to_parquet(CLEAN_PARQUET, index=False)
    print(f"Wrote Parquet: {CLEAN_PARQUET}")


if __name__ == "__main__":
    main()
