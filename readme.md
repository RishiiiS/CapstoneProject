# Telecom Customer Churn Analysis & Prediction

## Overview

This repository contains an end-to-end data analytics pipeline for a telecom churn project aimed at identifying customers likely to churn in the next quarter. The project integrates data engineering, exploratory data analysis (EDA), KPI framework development, and preparation for statistical modeling and dashboarding.

The objective is to enable data-driven decision-making for customer retention through structured analysis and actionable insights.

---

## Project Structure
├── data/
│   ├── raw/
│   │   └── iranian-telecom-churn.csv
│   └── processed/
│       ├── cleaned_data.csv
│       ├── final_kpi_data.csv
│       └── final_model_data.csv
│
├── notebooks/
│   ├── 01_extraction.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_eda.ipynb
│   └── 05_final_load_prep.ipynb
│
├── scripts/
│   └── etl_pipeline.py
│
├── docs/
│   ├── data_dictionary.md
│   └── cleaning_log.md
│
└── README.md

---

## Problem Statement

Customer churn is a major challenge in the telecom industry due to high competition and low switching costs. This project focuses on identifying customers at risk of churning and understanding the behavioral and operational factors driving churn.

---

## Objectives

- Analyze customer usage, engagement, and service quality  
- Identify key drivers of churn  
- Develop a KPI framework for monitoring customer health  
- Segment customers based on churn risk  
- Prepare datasets for dashboarding and predictive modeling  

---

## Data Description

The dataset contains telecom customer-level information including:

- Subscription details (e.g., subscription length)  
- Usage metrics (e.g., seconds of use, frequency of use, SMS activity)  
- Service quality indicators (e.g., call failures)  
- Billing information (e.g., charge amount)  
- Target variable: `churn`  

After processing, the dataset contains approximately **3,150 rows and 26 columns**.

---

## Data Engineering (M2)

A structured ETL pipeline was implemented to ensure data quality and consistency.

### Key Steps:
- Handling missing values using appropriate statistical methods  
- Removing duplicate records  
- Standardizing column names (snake_case)  
- Correcting data types  
- Validating usage fields without distorting distributions  
- Standardizing categorical values  

### Outputs:
- Cleaned dataset: `data/processed/cleaned_data.csv`  
- Data dictionary: `docs/data_dictionary.md`  
- Cleaning log: `docs/cleaning_log.md`  

---

## Exploratory Data Analysis & KPI Framework (M3)

EDA was performed to uncover patterns and relationships influencing churn.

### Analysis Includes:
- Univariate analysis (distributions, outliers)  
- Bivariate analysis (feature vs churn comparisons)  
- Segment analysis (usage, engagement, service quality)  
- Correlation analysis  

### KPI Framework:

- **Churn Rate** → Customer retention performance  
- **Usage Intensity** → seconds_of_use / subscription_length  
- **Engagement Intensity** → frequency_of_use / subscription_length  
- **SMS Intensity** → frequency_of_sms / subscription_length  
- **Call Failure Rate** → call_failures / frequency_of_use  

These KPIs provide meaningful insights into customer behavior and churn risk.

---

## Final Data Outputs

### 1. Cleaned Dataset  
`data/processed/cleaned_data.csv`  
- Fully cleaned and validated  
- Used for EDA and feature engineering  

### 2. KPI Dataset (Dashboard Use)  
`data/processed/final_kpi_data.csv`  
- Contains original + derived KPI features  
- Includes segmentation and monitoring fields  
- Used for Tableau dashboard  

### 3. Modeling Dataset (M4 Use)  
`data/processed/final_model_data.csv`  
- Excludes leakage-prone features:
  - `status`
  - `status_inactive_flag`
  - `complaints`
  - `complaints_flag`  
- Prepared for statistical modeling and machine learning  

---

## Leakage Handling

Certain variables (e.g., `status`, `complaints`) show strong correlation with churn and may act as lagging indicators.

To ensure model reliability:
- These features are retained in the KPI dataset for monitoring  
- These features are removed from the modeling dataset  

This separation prevents data leakage and ensures unbiased model performance.

---

## Key Insights

- Low engagement customers have significantly higher churn risk  
- High call failure rates strongly influence churn  
- Short subscription duration is a major churn indicator  
- Behavioral metrics are stronger predictors than static attributes  
- Specific customer segments contribute disproportionately to churn  

---

## Notebooks

- `01_extraction.ipynb` → Data loading and inspection  
- `02_cleaning.ipynb` → Data cleaning and preprocessing  
- `03_eda.ipynb` → Exploratory analysis and insights  
- `05_final_load_prep.ipynb` → KPI creation and dataset preparation  

All notebooks are executed and include outputs for validation.

---

## Run the Pipeline

```bash
./.venv/bin/python scripts/etl_pipeline.py

## Next Steps

- Apply statistical models for churn prediction  
- Build and publish Tableau dashboard  
- Generate business recommendations and impact analysis  

---

## Conclusion

This project delivers a structured and scalable approach to telecom churn analysis. By combining data engineering, exploratory analysis, and KPI-driven insights, it provides a strong foundation for predictive modeling and data-driven customer retention strategies.
