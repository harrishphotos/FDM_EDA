## NYC Yellow Taxi EDA – Project Snapshot

### Status at a glance

- **Sampling**: Completed. 100k-row representative sample created from monthly Parquet files.
- **Profiling**: Completed (see `Docs/raw_profile.md`).
- **Cleaning (pandas)**: Completed and verified (see `Docs/cleaning_rules.md`, `Docs/cleaning_report.md`, `Docs/verification_report.md`).

### Datasets in this repo

- **`NYC_YELLOW_TAXI_RAW.csv`**: 100,000 sampled rows; direct TLC schema columns as per `Docs/data_dictionary_trip_records_yellow-2.pdf`. Contains unstandardized codes, possible negatives/zero durations, and unadjusted totals.
- **`NYC_YELLOW_TAXI_CLEAN.csv`**: 97,139 rows after cleaning. Includes:
  - Sanitized domains (e.g., `VendorID`∈{1,2}, `payment_type`∈{1..6} or null).
  - Validated times (`dropoff ≥ pickup`, duration ≤ 24h; zero-minute kept only if distance>0).
  - Distance range constrained to [0, 200].
  - Fees/surcharges negatives set to null; totals reconciled to component sum (±0.01).
  - Deduplicated on key trip fields.
  - Zone enrichment: `PU_Borough`, `PU_Zone`, `PU_service_zone`, `DO_Borough`, `DO_Zone`, `DO_service_zone` from `Docs/taxi_zone_lookup.csv`.
  - Derived: `trip_duration_min`.

### Key scripts

- **`datasampling.py`**: Reservoir sample from monthly Parquet to create a 100k-row dataset (historical step).
- **`datacleaning.py`**: Pandas cleaning pipeline implementing `Docs/cleaning_rules.md`; writes `NYC_YELLOW_TAXI_CLEAN.csv` and `Docs/cleaning_report.md`.
- **`scripts/verify_cleaning.py`**: Post-clean checks; writes `Docs/verification_report.md` (all checks PASS).

### References

- **Data dictionary**: `Docs/data_dictionary_trip_records_yellow-2.pdf`
- **Zone lookup**: `Docs/taxi_zone_lookup.csv`
