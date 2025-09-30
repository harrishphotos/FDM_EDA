# NYC Yellow Taxi Raw Profile

Generated: 2025-09-30T21:20:05

**Total rows**: 100,000

## Schema

- VendorID: BIGINT
- tpep_pickup_datetime: TIMESTAMP
- tpep_dropoff_datetime: TIMESTAMP
- passenger_count: DOUBLE
- trip_distance: DOUBLE
- RatecodeID: DOUBLE
- store_and_fwd_flag: VARCHAR
- PULocationID: BIGINT
- DOLocationID: BIGINT
- payment_type: BIGINT
- fare_amount: DOUBLE
- extra: DOUBLE
- mta_tax: DOUBLE
- tip_amount: DOUBLE
- tolls_amount: DOUBLE
- improvement_surcharge: DOUBLE
- total_amount: DOUBLE
- congestion_surcharge: DOUBLE
- airport_fee: DOUBLE

## Null counts

- passenger_count: 11,412 (11.41%)
- RatecodeID: 11,412 (11.41%)
- store_and_fwd_flag: 11,412 (11.41%)
- congestion_surcharge: 11,412 (11.41%)
- airport_fee: 11,412 (11.41%)

## Enumerations

- VendorID
  - 2: 76,191
  - 1: 23,536
  - 7: 262
  - 6: 11
- RatecodeID
  - 1.0: 83,005
  - None: 11,412
  - 2.0: 3,395
  - 99.0: 911
  - 5.0: 759
  - 3.0: 307
  - 4.0: 211
- payment_type
  - 1: 72,529
  - 2: 13,520
  - 0: 11,412
  - 4: 1,852
  - 3: 687
- store_and_fwd_flag
  - N: 88,150
  - None: 11,412
  - Y: 438

## Numeric ranges

- passenger_count: min=0.0, max=8.0
- trip_distance: min=0.0, max=222376.21
- fare_amount: min=-248.0, max=800.0
- extra: min=-7.5, max=12.5
- mta_tax: min=-0.5, max=0.8
- tip_amount: min=-50.05, max=99.99
- tolls_amount: min=-84.0, max=50.0
- improvement_surcharge: min=-1.0, max=1.0
- total_amount: min=-230.01, max=801.0
- congestion_surcharge: min=-2.5, max=2.5
- airport_fee: min=-1.75, max=6.75

## Duration anomalies

- dropoff before pickup: 6
- zero-minute trips: 1,105
- trips over 24 hours: 3

## Negative/invalid amounts (row counts)

- fare_amount < 0: 2,740
- tip_amount < 0: 2
- tolls_amount < 0: 100
- extra < 0: 722
- mta_tax < 0: 1,356
- improvement_surcharge < 0: 1,424
- congestion_surcharge < 0: 1,118
- airport_fee < 0: 246
- total_amount < 0: 1,470

## Invalid codes (per data dictionary)

- VendorID not in (1,2): 273
- RatecodeID not in (1..6): 911
- payment_type not in (1..6): 11,412
- store_and_fwd_flag not in ('Y','N'): 0

## Location mapping coverage

- Unmapped PULocationID rows: 0
- Unmapped DOLocationID rows: 0
