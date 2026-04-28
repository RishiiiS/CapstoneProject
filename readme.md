# Telecom Churn Data Pipeline

This repository contains the M2 data engineering deliverables for a telecom churn project focused on identifying customers likely to churn in the next quarter.

## Project Structure

```text
project-name/
├── data/
│   ├── raw/
│   │   └── iranian-telecom-churn.csv
│   └── processed/
│       └── cleaned_data.csv
├── notebooks/
│   ├── 01_extraction.ipynb
│   └── 02_cleaning.ipynb
├── scripts/
│   └── etl_pipeline.py
├── docs/
│   ├── data_dictionary.md
│   └── cleaning_log.md
└── README.md
```

## Current State

- Raw dataset loaded from `data/raw/iranian-telecom-churn.csv`
- Cleaned dataset saved to `data/processed/cleaned_data.csv`
- Data dictionary stored in `docs/data_dictionary.md`
- Cleaning decisions and audit trail stored in `docs/cleaning_log.md`

## Cleaning Rules

- Standardize column names to snake_case
- Remove exact duplicate rows only
- Validate integer telecom usage fields without coercive winsorization
- Standardize categorical labels for `tariff_plan`, `status`, `age_group`, and `complaints`
- Preserve valid high-usage observations and log outlier review instead of capping values

## Run The Pipeline

```bash
./.venv/bin/python scripts/etl_pipeline.py
```

## Readiness Notes

- The cleaned dataset is structurally ready for EDA.
- Before modeling, review `status` and `complaints` for possible target leakage against the churn observation window.
- Before business KPI reporting, confirm whether `charge_amount` is a true revenue field or a billing tier/category.
