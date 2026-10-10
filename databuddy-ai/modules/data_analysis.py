"""Dataset summaries and data-quality measurements."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd


def dataset_metrics(frame: pd.DataFrame) -> dict[str, int]:
    """Return the headline counts shown in the overview."""
    return {
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum()),
    }


def quality_report(frame: pd.DataFrame) -> pd.DataFrame:
    """Describe column types, completeness, distinct values, and basic statistics."""
    row_count = len(frame)
    rows: list[dict[str, object]] = []

    for column in frame.columns:
        series = frame[column]
        missing = int(series.isna().sum())
        summary: dict[str, object] = {}

        if pd.api.types.is_numeric_dtype(series):
            numeric = series.dropna()
            if not numeric.empty:
                summary = {
                    "mean": _json_number(numeric.mean()),
                    "median": _json_number(numeric.median()),
                    "min": _json_number(numeric.min()),
                    "max": _json_number(numeric.max()),
                }
        else:
            non_missing = series.dropna()
            if not non_missing.empty:
                mode = non_missing.mode()
                summary = {
                    "most_common": str(mode.iloc[0]) if not mode.empty else None,
                    "most_common_count": int(non_missing.value_counts().iloc[0]),
                }

        rows.append(
            {
                "column": str(column),
                "data_type": str(series.dtype),
                "missing_count": missing,
                "missing_percent": round((missing / row_count * 100) if row_count else 0.0, 2),
                "unique_values": int(series.nunique(dropna=True)),
                "basic_summary": json.dumps(summary, ensure_ascii=False),
            }
        )

    return pd.DataFrame(rows)


def statistical_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Return readable descriptive statistics for all columns."""
    if frame.empty:
        return pd.DataFrame()
    summary = frame.describe(include="all").transpose().reset_index(names="column")
    return summary.replace({np.nan: None})


def numeric_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    """Return Pearson correlations for numeric columns, or an empty table."""
    numeric = frame.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        return pd.DataFrame()
    return numeric.corr()


def simple_explanation(frame: pd.DataFrame) -> dict[str, object]:
    """Build beginner-friendly observations using only calculated dataset values."""
    metrics = dataset_metrics(frame)
    numeric = frame.select_dtypes(include="number")
    categorical = frame.select_dtypes(exclude="number")

    issues: list[str] = []
    if metrics["missing_cells"]:
        issues.append(
            f"There are {metrics['missing_cells']} missing cells. A missing cell is a blank value."
        )
    if metrics["duplicate_rows"]:
        issues.append(
            f"There are {metrics['duplicate_rows']} duplicate rows. These are repeated records."
        )
    if not issues:
        issues.append("No missing cells or duplicate rows were found.")

    observations: list[str] = []
    if not numeric.empty:
        means = numeric.mean().dropna()
        if not means.empty:
            column = str(means.idxmax())
            observations.append(
                f"Among the numeric columns, {column} has the highest average "
                f"({means.max():,.2f})."
            )
        spread = numeric.std().dropna()
        if not spread.empty:
            column = str(spread.idxmax())
            observations.append(
                f"{column} varies the most from row to row, based on its standard deviation."
            )
    if not observations:
        observations.append(
            "There are no numeric columns, so averages and numeric charts are not available."
        )

    suggestions: list[str] = []
    if not numeric.empty:
        suggestions.append(f"Try a histogram to see the spread of {numeric.columns[0]}.")
    if not categorical.empty:
        suggestions.append(f"Try a bar chart to compare values in {categorical.columns[0]}.")
    if numeric.shape[1] >= 2:
        suggestions.append("Try a scatter plot or correlation heatmap to compare numeric columns.")
    if not suggestions:
        suggestions.append("Try a bar chart to compare how often each category appears.")

    next_steps: list[str] = []
    if metrics["missing_cells"]:
        next_steps.append("Review which columns have blanks, then choose how to fill or remove them.")
    if metrics["duplicate_rows"]:
        next_steps.append("Check the repeated rows and remove them if they are accidental copies.")
    if not next_steps:
        next_steps.append("Choose a question about the dataset and explore it with a chart.")
    next_steps.append("Compare two columns to look for patterns before drawing conclusions.")
    next_steps.append("Download a report so you can keep a copy of these findings.")

    return {
        "summary": (
            f"Your dataset has {metrics['rows']:,} rows and {metrics['columns']:,} columns. "
            f"It contains {metrics['missing_cells']:,} missing cells and "
            f"{metrics['duplicate_rows']:,} duplicate rows."
        ),
        "quality_issues": issues,
        "observations": observations,
        "visualizations": suggestions[:3],
        "next_steps": next_steps[:3],
        "metrics": metrics,
    }


def _json_number(value: object) -> int | float | None:
    """Convert NumPy/Pandas numeric values to JSON-safe Python numbers."""
    if pd.isna(value):
        return None
    number = float(value)
    return int(number) if number.is_integer() else round(number, 4)
