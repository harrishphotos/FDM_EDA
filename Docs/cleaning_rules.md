## NYC Yellow Taxi – Cleaning Rules (Pandas)

Scope: Applies to `NYC_YELLOW_TAXI_RAW.csv` (~100k rows). Based on TLC Yellow Trip Records dictionary and profiling observations.

### 1) Column types

- Cast IDs/counts to nullable integers: `VendorID`, `PULocationID`, `DOLocationID`, `payment_type`, `RatecodeID`, `passenger_count` → `Int64`.
- Cast monetary to float: `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `congestion_surcharge`, `airport_fee`, `trip_distance` → float64.
- Timestamps: parse `tpep_pickup_datetime`, `tpep_dropoff_datetime` as timezone-naive `datetime64[ns]`.
- `store_and_fwd_flag`: uppercase string, limit to {Y,N} else null.

### 2) Valid domains (dictionary-aligned)

- VendorID ∈ {1,2}. Rows with other values → dropped.
- RatecodeID ∈ {1,2,3,4,5,6}. Others (e.g., 99) → null.
- payment_type ∈ {1,2,3,4,5,6}. Observed 0 → null.
- store_and_fwd_flag ∈ {Y,N} only; others → null.

### 3) Datetime sanity

- Drop rows with `dropoff < pickup`.
- Compute `trip_duration_min = (dropoff - pickup).dt.total_seconds()/60`.
- Drop rows with `trip_duration_min > 24*60`.
- Zero-minute trips: keep only if `trip_distance > 0`; otherwise drop.

### 4) Distance sanity

- Drop rows with `trip_distance < 0`.
- Drop rows with `trip_distance > 200` (extreme outliers for NYC yellow trips).

### 5) Monetary fields and totals

- For rows with `payment_type` ∈ {4=Dispute, 6=Voided}: allow negative `fare_amount`/`total_amount` (adjustments). Do not coerce to positive.
- For other payment types (1,2,3,5):
  - Drop rows with `fare_amount < 0` or `total_amount < 0`.
- Component fees/surcharges should be non-negative. If any of `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `congestion_surcharge`, `airport_fee` are negative, set to null.
- Recompute `computed_total = fare_amount + extra + mta_tax + tip_amount + tolls_amount + improvement_surcharge + coalesce(congestion_surcharge,0) + coalesce(airport_fee,0)`.
- If `|total_amount - computed_total| > 0.01`, replace `total_amount` with `computed_total`.

### 6) Passenger count

- Cast to Int64; values <0 → null; values >6 → null. Keep nulls (no imputation).

### 7) Deduplication

- Remove exact duplicates using this subset:
  - `VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, PULocationID, DOLocationID, trip_distance, fare_amount, payment_type`.

### 8) Zone mapping

- Join `Docs/taxi_zone_lookup.csv` on `PULocationID` and `DOLocationID` to append:
  - Pickup: `PU_Borough, PU_Zone, PU_service_zone`
  - Dropoff: `DO_Borough, DO_Zone, DO_service_zone`
- Keep original ID columns.

### 9) Output

- Save cleaned CSV: `NYC_YELLOW_TAXI_CLEAN.csv` with all original columns plus derived:
  - `trip_duration_min`, `PU_Borough`, `PU_Zone`, `PU_service_zone`, `DO_Borough`, `DO_Zone`, `DO_service_zone`.
- Save a small `Docs/cleaning_report.md` with row counts per step and basic distributions.

### 10) Verification (post-clean)

- No `VendorID` outside {1,2}.
- `RatecodeID` null or in {1..6}.
- `payment_type` null or in {1..6} (no zeros).
- `store_and_fwd_flag` null or in {Y,N}.
- `trip_distance` ∈ [0,200].
- `dropoff >= pickup`; `trip_duration_min <= 1440`; zero-minute implies `trip_distance > 0`.
- For payment_type ∉ {4,6}: `fare_amount >= 0` and `total_amount >= 0`.
- Fees/surcharges/tips/tolls are ≥0 or null.
- `total_amount ≈ computed_total` within 0.01.
- `PU_Zone` and `DO_Zone` not null (full mapping).
