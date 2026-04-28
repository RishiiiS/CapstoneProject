# Telecom Churn Data Dictionary

## Dataset Overview

This document describes the cleaned telecom churn dataset used for downstream EDA, statistical analysis, and churn modeling.

| Property | Value |
|---|---|
| Source file | `data/raw/iranian-telecom-churn.csv` |
| Cleaned file | `data/processed/cleaned_data.csv` |
| Row count | 3150 |
| Column count | 13 |
| Target column | `churn` |
| Target meaning | `1` = churned, `0` = retained |

## Schema

| Column | Type | Role | Description | Valid values / range |
|---|---|---|---|---|
| `id` | `int64` | Identifier | Unique customer identifier | 1 to 3150 |
| `subscription_length` | `int64` | Feature | Subscription tenure in months | 3 to 47 |
| `charge_amount` | `int64` | Feature | Customer billing tier or charge category from source system | 0 to 10 |
| `seconds_of_use` | `int64` | Feature | Total observed call usage in seconds | 0 to 17090 |
| `frequency_of_use` | `int64` | Feature | Total service usage events | 0 to 255 |
| `frequency_of_sms` | `int64` | Feature | Total SMS usage events | 0 to 522 |
| `distinct_called_numbers` | `int64` | Feature | Number of unique called numbers | 0 to 97 |
| `call_failures` | `int64` | Feature | Number of failed call attempts | 0 to 36 |
| `tariff_plan` | `string` | Feature | Customer tariff plan | `A`, `B` |
| `status` | `string` | Feature | Current account status at data capture | `Active`, `Inactive` |
| `age_group` | `string` | Feature | Age band | `Under 30`, `30-40`, `Over 40` |
| `complaints` | `string` | Feature | Whether the customer filed complaints | `Y`, `N` |
| `churn` | `int64` | Target | Churn outcome label | `0`, `1` |

## Data Quality Notes

- Missing values: none in the cleaned dataset.
- Duplicate rows: none in the raw or cleaned dataset.
- Column naming: standardized to snake_case in the cleaned dataset.
- Category standardization: categorical labels are trimmed and validated against expected values.
- Outliers: IQR bounds are reviewed and logged in [cleaning_log.md](/Users/kanishkranjan/Desktop/CapstoneProject/docs/cleaning_log.md), but values are not capped to avoid distorting valid telecom behavior.

## Modeling and Analysis Notes

- The target is moderately imbalanced: 2655 retained vs 495 churned customers.
- `charge_amount` should be treated as a source billing category unless the business confirms it is true monetary revenue.
- `status` and `complaints` may be highly predictive, but they should be reviewed for temporal leakage before modeling because they may reflect information close to or after churn.
