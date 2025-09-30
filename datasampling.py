"""
Purpose:
- Create a 100,000-row representative sample from NYC Yellow Taxi Parquet files
  spanning the last 3 years using DuckDB's reservoir sampling.

Key ideas for simplicity and safety:
- Read Parquet directly with DuckDB (no Pandas) to avoid loading full data in memory.
- Use a single global reservoir sample so busy months naturally contribute more rows.
- Fix a random seed and single-thread execution for reproducibility.

Output:
- Writes the final dataset NYC_YELLOW_TAXI.csv.
"""

import os
import importlib

# Absolute path to the directory that contains all monthly Parquet files
DATA_DIRECTORY = "/Users/harish/FDM - Taxi/Datasets"

# File pattern for all monthly Parquet files
PARQUET_GLOB = os.path.join(DATA_DIRECTORY, "yellow_tripdata_*.parquet")

# Desired number of rows in the final sample
SAMPLE_SIZE = 100_000

# Seed for repeatable sampling
RANDOM_SEED = 42

# Output CSV path
OUTPUT_CSV = os.path.join("/Users/harish/FDM - Taxi", "NYC_YELLOW_TAXI.csv")


def main() -> None:

    # Connect to DuckDB (in-memory)
    duckdb = importlib.import_module("duckdb")

    con = duckdb.connect(database=":memory:")

    # Set to one thread to ensure deterministic sampling order
    con.execute("SET threads = 1;")


    # Build the global reservoir sampling SQL query
    # read_parquet supports globbing and reads Parquet lazily/efficiently.
    # USING SAMPLE RESERVOIR(N ROWS) selects exactly N rows overall.
    # REPEATABLE(seed) makes the sample deterministic.
    sampling_query = f"""
        SELECT *
        FROM read_parquet('{PARQUET_GLOB}')
        USING SAMPLE reservoir({SAMPLE_SIZE} ROWS)
        REPEATABLE({RANDOM_SEED})
    """

    # Stream results directly out to CSV
    # COPY executes the sampling query inside DuckDB and writes rows as they stream,
    # avoiding a large materialized result in Python memory.
    copy_sql = f"COPY (\n{sampling_query}\n) TO '{OUTPUT_CSV}' (HEADER, DELIMITER ',');"

    # Execute COPY in one go; DuckDB handles Parquet scanning and sampling efficiently
    con.execute(copy_sql)

    # Clean up the connection
    con.close()

    print(f"Wrote {SAMPLE_SIZE} sampled rows to: {OUTPUT_CSV}")




if __name__ == "__main__":
    main()


