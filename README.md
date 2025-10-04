## NYC Yellow Taxi EDA – Project Snapshot

### Status at a glance

- **Sampling**: Completed. 100k-row representative sample created from monthly Parquet files.
- **Profiling**: Completed (see `Docs/raw_profile.md`).
- **Cleaning (pandas)**: Completed and verified (see `Docs/cleaning_rules.md`, `Docs/cleaning_report.md`, `Docs/verification_report.md`).
- **Machine Learning**: Completed. Fare and tip prediction models trained and deployed (see `Docs/model_deployment.md`).
- **Dashboard**: Completed. 10-tab interactive Streamlit dashboard with predictions (see `streamlit_app/`).

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
- **`datamodeling.py`**: Train ML models for fare and tip prediction; writes `fare_model.pkl` and `tip_model.pkl`.
- **`scripts/verify_cleaning.py`**: Post-clean checks; writes `Docs/verification_report.md` (all checks PASS).
- **`streamlit_app/app.py`**: Main dashboard application with 10 interactive tabs.
- **`streamlit_app/predictions.py`**: ML prediction interfaces for fare and tip estimation.

### Machine Learning Models

- **Fare Prediction Model** (`fare_model.pkl`): Random Forest Regressor
  - RMSE: $9.23 | R² Score: 0.7710
  - Predicts fare amount based on trip distance, duration, passenger count, and pickup hour
  - Trip distance accounts for 85% of prediction importance
- **Tip Prediction Model** (`tip_model.pkl`): Random Forest Classifier
  - Accuracy: 66.5% | F1-Score: 0.7847
  - Predicts likelihood of receiving tip > $2
  - Trip duration and distance are strongest predictors

### Interactive Dashboard Features

The Streamlit dashboard (`streamlit_app/`) provides 10 interactive tabs:

1. **Overview**: KPIs, payment mix, rate code distribution
2. **Trends**: Monthly trips, revenue, and average fare trends
3. **Time Analysis**: Hourly patterns, optimal earning windows
4. **Map**: Interactive choropleth heatmap of all 263 NYC taxi zones
5. **Hotspots**: Treemap visualization by borough and zone
6. **Zones**: Top pickup/dropoff location rankings
7. **Flows**: Origin-destination route analysis with Sankey diagrams
8. **Airports**: JFK/LaGuardia/Newark trip patterns
9. **Fare Prediction**: ML-powered fare estimation with similar trip comparison
10. **Tip Prediction**: ML-powered tip likelihood with hourly analysis

### Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Train ML models (if not already trained)
python datamodeling.py

# Run Streamlit dashboard
cd streamlit_app
streamlit run app.py
```

### References

- **Data dictionary**: `Docs/data_dictionary_trip_records_yellow-2.pdf`
- **Zone lookup**: `Docs/taxi_zone_lookup.csv`
- **Model deployment guide**: `Docs/model_deployment.md`
