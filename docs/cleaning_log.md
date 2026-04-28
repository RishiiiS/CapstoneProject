# Cleaning Log

## Summary

- Raw rows: 3150
- Cleaned rows: 3150
- Column count: 13
- Duplicate rows removed: 0
- Missing values remaining: none

## Transformations Applied

- `2026-04-28 21:55:53` Data Loading: Loaded 3150 rows and 13 columns from data/raw/iranian-telecom-churn.csv
- `2026-04-28 21:55:53` Column Standardization: Converted 13 columns to snake_case format
- `2026-04-28 21:55:53` Duplicate Removal: No duplicate rows found
- `2026-04-28 21:55:53` Data Types: Validated integer business fields and normalized categorical string fields
- `2026-04-28 21:55:53` Category Standardization: Standardized telecom category labels and validated expected levels
- `2026-04-28 21:55:53` Schema Validation: Verified all required churn columns are present
- `2026-04-28 21:55:53` Missing Values: Verified dataset contains no missing values
- `2026-04-28 21:55:53` Outlier Review: Profiled numeric outliers with IQR bounds without altering source values
- `2026-04-28 21:55:53` Data Save: Saved cleaned data to data/processed/cleaned_data.csv: 3150 rows x 13 columns

## Numeric Ranges

| Column | Min | Max |
|---|---:|---:|
| subscription_length | 3.0 | 47.0 |
| charge_amount | 0.0 | 10.0 |
| seconds_of_use | 0.0 | 17090.0 |
| frequency_of_use | 0.0 | 255.0 |
| frequency_of_sms | 0.0 | 522.0 |
| distinct_called_numbers | 0.0 | 97.0 |
| call_failures | 0.0 | 36.0 |
| churn | 0.0 | 1.0 |

## Category Levels

| Column | Allowed values |
|---|---|
| tariff_plan | A, B |
| status | Active, Inactive |
| age_group | 30-40, Over 40, Under 30 |
| complaints | N, Y |

## Outlier Review

Outliers were profiled with IQR bounds and retained because these fields represent valid telecom usage and service behavior.

| Column | Lower bound | Upper bound | Flagged rows |
|---|---:|---:|---:|
| subscription_length | 18.0 | 50.0 | 282 |
| charge_amount | -1.5 | 2.5 | 370 |
| seconds_of_use | -6239.25 | 14108.75 | 200 |
| frequency_of_use | -75.0 | 197.0 | 129 |
| frequency_of_sms | -115.5 | 208.5 | 368 |
| distinct_called_numbers | -26.0 | 70.0 | 77 |
| call_failures | -15.5 | 28.5 | 47 |

## Target Distribution

- Churn = 0: 2655
- Churn = 1: 495

## Assumptions and Risks

- No values were imputed because the source dataset contains no missing values.
- No outlier capping was applied to avoid distorting valid customer behavior.
- `status` and `complaints` remain in the dataset but should be reviewed for temporal leakage before modeling.
