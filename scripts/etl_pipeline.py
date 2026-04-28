"""
ETL pipeline for the Iranian telecom churn dataset.

The pipeline is intentionally conservative:
- preserve valid business values from the source file
- standardize schema and categorical formatting
- remove only exact duplicate rows
- log data quality findings for downstream review
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass
class QualitySummary:
    raw_rows: int
    cleaned_rows: int
    columns: int
    missing_values: dict[str, int]
    duplicate_rows_removed: int
    numeric_ranges: dict[str, dict[str, float]]
    categorical_levels: dict[str, list[str]]
    outlier_review: dict[str, dict[str, float | int]]


class ETLPipeline:
    """Reusable ETL pipeline for telecom churn data."""

    def __init__(
        self,
        raw_data_path: str,
        processed_data_path: str,
        markdown_log_path: str,
    ) -> None:
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.markdown_log_path = markdown_log_path
        self.transformation_log: list[dict[str, str]] = []
        self._setup_directories()

    def _setup_directories(self) -> None:
        for directory in {
            os.path.dirname(self.processed_data_path),
            os.path.dirname(self.markdown_log_path),
            "data/raw",
        }:
            if directory:
                os.makedirs(directory, exist_ok=True)
        print("[SETUP] Directories ready")

    def log_transformation(self, step_name: str, message: str) -> None:
        entry = {
            "step": step_name,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.transformation_log.append(entry)
        print(f"[LOG] {step_name}: {message}")

    def load_data(self) -> pd.DataFrame:
        print(f"\n{'=' * 50}")
        print("STEP 1: Loading Raw Data")
        print(f"{'=' * 50}")

        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Raw data file not found: {self.raw_data_path}")

        df = pd.read_csv(self.raw_data_path)
        if df.empty:
            raise ValueError("Loaded data is empty")

        self.log_transformation(
            "Data Loading",
            f"Loaded {len(df)} rows and {len(df.columns)} columns from {self.raw_data_path}",
        )
        return df

    @staticmethod
    def _standardize_name(column_name: str) -> str:
        name = column_name.strip().lower()
        name = re.sub(r"[\s\-]+", "_", name)
        name = re.sub(r"[^a-z0-9_]", "", name)
        name = re.sub(r"_+", "_", name)
        return name.strip("_")

    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        original_columns = list(df.columns)
        df = df.copy()
        df.columns = [self._standardize_name(column) for column in df.columns]

        changed = sum(1 for before, after in zip(original_columns, df.columns) if before != after)
        self.log_transformation(
            "Column Standardization",
            f"Converted {changed} columns to snake_case format",
        )
        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        duplicate_count = int(df.duplicated().sum())
        if duplicate_count:
            df = df.drop_duplicates().reset_index(drop=True)
            self.log_transformation("Duplicate Removal", f"Removed {duplicate_count} exact duplicate rows")
        else:
            self.log_transformation("Duplicate Removal", "No duplicate rows found")
        return df, duplicate_count

    def _fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        integer_columns = [
            "id",
            "subscription_length",
            "charge_amount",
            "seconds_of_use",
            "frequency_of_use",
            "frequency_of_sms",
            "distinct_called_numbers",
            "call_failures",
            "churn",
        ]
        categorical_columns = ["tariff_plan", "status", "age_group", "complaints"]

        for column in integer_columns:
            if column in df.columns:
                series = pd.to_numeric(df[column], errors="raise")
                if series.isnull().any():
                    raise ValueError(f"Unexpected nulls introduced while parsing '{column}'")
                df[column] = series.astype("int64")

        for column in categorical_columns:
            if column in df.columns:
                df[column] = df[column].astype("string").str.strip()

        self.log_transformation(
            "Data Types",
            "Validated integer business fields and normalized categorical string fields",
        )
        return df

    def _standardize_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        category_maps = {
            "tariff_plan": {"a": "A", "b": "B"},
            "status": {"active": "Active", "inactive": "Inactive"},
            "complaints": {"y": "Y", "n": "N"},
        }

        for column, mapping in category_maps.items():
            if column in df.columns:
                normalized = df[column].str.strip().str.lower()
                unknown_values = sorted(set(normalized.dropna().unique()) - set(mapping.keys()))
                if unknown_values:
                    raise ValueError(f"Unexpected values found in '{column}': {unknown_values}")
                df[column] = normalized.map(mapping).astype("string")

        if "age_group" in df.columns:
            normalized = df["age_group"].str.strip()
            valid_values = {"Under 30", "30-40", "Over 40"}
            unknown_values = sorted(set(normalized.dropna().unique()) - valid_values)
            if unknown_values:
                raise ValueError(f"Unexpected values found in 'age_group': {unknown_values}")
            df["age_group"] = normalized.astype("string")

        self.log_transformation(
            "Category Standardization",
            "Standardized telecom category labels and validated expected levels",
        )
        return df

    def _validate_required_columns(self, df: pd.DataFrame) -> None:
        required_columns = {
            "id",
            "subscription_length",
            "charge_amount",
            "seconds_of_use",
            "frequency_of_use",
            "frequency_of_sms",
            "distinct_called_numbers",
            "call_failures",
            "tariff_plan",
            "status",
            "age_group",
            "complaints",
            "churn",
        }
        missing_columns = sorted(required_columns - set(df.columns))
        if missing_columns:
            raise ValueError(f"Required columns missing after cleaning: {missing_columns}")
        self.log_transformation("Schema Validation", "Verified all required churn columns are present")

    def _check_missing_values(self, df: pd.DataFrame) -> None:
        null_counts = df.isnull().sum()
        total_nulls = int(null_counts.sum())
        if total_nulls:
            missing = {column: int(count) for column, count in null_counts[null_counts > 0].items()}
            raise ValueError(f"Missing values remain after cleaning: {missing}")
        self.log_transformation("Missing Values", "Verified dataset contains no missing values")

    def _profile_outliers(self, df: pd.DataFrame) -> dict[str, dict[str, float | int]]:
        outlier_review: dict[str, dict[str, float | int]] = {}
        numeric_columns = [
            "subscription_length",
            "charge_amount",
            "seconds_of_use",
            "frequency_of_use",
            "frequency_of_sms",
            "distinct_called_numbers",
            "call_failures",
        ]

        for column in numeric_columns:
            q1 = float(df[column].quantile(0.25))
            q3 = float(df[column].quantile(0.75))
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outlier_count = int(((df[column] < lower_bound) | (df[column] > upper_bound)).sum())
            outlier_review[column] = {
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2),
                "outlier_count": outlier_count,
            }

        self.log_transformation(
            "Outlier Review",
            "Profiled numeric outliers with IQR bounds without altering source values",
        )
        return outlier_review

    def build_quality_summary(
        self,
        raw_df: pd.DataFrame,
        cleaned_df: pd.DataFrame,
        duplicate_rows_removed: int,
        outlier_review: dict[str, dict[str, float | int]],
    ) -> QualitySummary:
        numeric_columns = [
            "subscription_length",
            "charge_amount",
            "seconds_of_use",
            "frequency_of_use",
            "frequency_of_sms",
            "distinct_called_numbers",
            "call_failures",
            "churn",
        ]
        categorical_columns = ["tariff_plan", "status", "age_group", "complaints"]

        numeric_ranges = {
            column: {
                "min": float(cleaned_df[column].min()),
                "max": float(cleaned_df[column].max()),
            }
            for column in numeric_columns
        }
        categorical_levels = {
            column: sorted(cleaned_df[column].dropna().unique().tolist())
            for column in categorical_columns
        }
        missing_values = {column: int(count) for column, count in cleaned_df.isnull().sum().items()}

        return QualitySummary(
            raw_rows=len(raw_df),
            cleaned_rows=len(cleaned_df),
            columns=len(cleaned_df.columns),
            missing_values=missing_values,
            duplicate_rows_removed=duplicate_rows_removed,
            numeric_ranges=numeric_ranges,
            categorical_levels=categorical_levels,
            outlier_review=outlier_review,
        )

    def clean_data(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int, dict[str, dict[str, float | int]]]:
        print(f"\n{'=' * 50}")
        print("STEP 2: Cleaning Data")
        print(f"{'=' * 50}")

        df = self._standardize_column_names(df)
        df, duplicate_rows_removed = self._remove_duplicates(df)
        df = self._fix_data_types(df)
        df = self._standardize_categories(df)
        self._validate_required_columns(df)
        self._check_missing_values(df)
        outlier_review = self._profile_outliers(df)

        print(f"✓ Data cleaning complete: {df.shape[0]} rows x {df.shape[1]} columns")
        return df, duplicate_rows_removed, outlier_review

    def save_data(self, df: pd.DataFrame) -> str:
        print(f"\n{'=' * 50}")
        print("STEP 3: Saving Cleaned Data")
        print(f"{'=' * 50}")

        df.to_csv(self.processed_data_path, index=False)
        self.log_transformation(
            "Data Save",
            f"Saved cleaned data to {self.processed_data_path}: {len(df)} rows x {len(df.columns)} columns",
        )
        return self.processed_data_path

    def save_markdown_log(self, summary: QualitySummary) -> None:
        churn_counts = pd.read_csv(self.processed_data_path)["churn"].value_counts().sort_index()
        lines = [
            "# Cleaning Log",
            "",
            "## Summary",
            "",
            f"- Raw rows: {summary.raw_rows}",
            f"- Cleaned rows: {summary.cleaned_rows}",
            f"- Column count: {summary.columns}",
            f"- Duplicate rows removed: {summary.duplicate_rows_removed}",
            "- Missing values remaining: none",
            "",
            "## Transformations Applied",
            "",
        ]
        for entry in self.transformation_log:
            lines.append(f"- `{entry['timestamp']}` {entry['step']}: {entry['message']}")

        lines.extend(
            [
                "",
                "## Numeric Ranges",
                "",
                "| Column | Min | Max |",
                "|---|---:|---:|",
            ]
        )
        for column, stats in summary.numeric_ranges.items():
            lines.append(f"| {column} | {stats['min']} | {stats['max']} |")

        lines.extend(
            [
                "",
                "## Category Levels",
                "",
                "| Column | Allowed values |",
                "|---|---|",
            ]
        )
        for column, levels in summary.categorical_levels.items():
            lines.append(f"| {column} | {', '.join(levels)} |")

        lines.extend(
            [
                "",
                "## Outlier Review",
                "",
                "Outliers were profiled with IQR bounds and retained because these fields represent valid telecom usage and service behavior.",
                "",
                "| Column | Lower bound | Upper bound | Flagged rows |",
                "|---|---:|---:|---:|",
            ]
        )
        for column, stats in summary.outlier_review.items():
            lines.append(
                f"| {column} | {stats['lower_bound']} | {stats['upper_bound']} | {stats['outlier_count']} |"
            )

        lines.extend(
            [
                "",
                "## Target Distribution",
                "",
                f"- Churn = 0: {int(churn_counts.get(0, 0))}",
                f"- Churn = 1: {int(churn_counts.get(1, 0))}",
                "",
                "## Assumptions and Risks",
                "",
                "- No values were imputed because the source dataset contains no missing values.",
                "- No outlier capping was applied to avoid distorting valid customer behavior.",
                "- `status` and `complaints` remain in the dataset but should be reviewed for temporal leakage before modeling.",
            ]
        )

        with open(self.markdown_log_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")
        print(f"✓ Markdown log saved to: {self.markdown_log_path}")

    def run_pipeline(self) -> pd.DataFrame:
        print(f"\n{'#' * 50}")
        print("# ETL PIPELINE STARTED")
        print(f"{'#' * 50}")

        try:
            raw_df = self.load_data()
            cleaned_df, duplicate_rows_removed, outlier_review = self.clean_data(raw_df)
            self.save_data(cleaned_df)
            quality_summary = self.build_quality_summary(
                raw_df=raw_df,
                cleaned_df=cleaned_df,
                duplicate_rows_removed=duplicate_rows_removed,
                outlier_review=outlier_review,
            )
            self.save_markdown_log(quality_summary)
            print(f"\n{'#' * 50}")
            print("# ETL PIPELINE COMPLETED SUCCESSFULLY")
            print(f"{'#' * 50}")
            return cleaned_df
        except Exception as exc:
            self.log_transformation("ERROR", str(exc))
            raise


def main() -> pd.DataFrame:
    pipeline = ETLPipeline(
        raw_data_path="data/raw/iranian-telecom-churn.csv",
        processed_data_path="data/processed/cleaned_data.csv",
        markdown_log_path="docs/cleaning_log.md",
    )
    return pipeline.run_pipeline()


if __name__ == "__main__":
    main()
