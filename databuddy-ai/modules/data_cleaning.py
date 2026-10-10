"""Non-destructive data cleaning operations."""

from __future__ import annotations

import pandas as pd

NUMERIC_STRATEGIES = ("mean", "median", "drop rows", "leave unchanged")
CATEGORICAL_STRATEGIES = ("most common value", "fill with 'Unknown'", "drop rows", "leave unchanged")


def clean_dataset(
    frame: pd.DataFrame,
    *,
    remove_duplicates: bool = True,
    numeric_strategy: str = "leave unchanged",
    categorical_strategy: str = "leave unchanged",
) -> pd.DataFrame:
    """Return a cleaned copy; never mutate the caller's original DataFrame."""
    if numeric_strategy not in NUMERIC_STRATEGIES:
        raise ValueError(f"Choose a numeric strategy from: {', '.join(NUMERIC_STRATEGIES)}.")
    if categorical_strategy not in CATEGORICAL_STRATEGIES:
        raise ValueError(
            f"Choose a categorical strategy from: {', '.join(CATEGORICAL_STRATEGIES)}."
        )

    cleaned = frame.copy(deep=True)
    if remove_duplicates:
        cleaned = cleaned.drop_duplicates().copy()

    if numeric_strategy == "drop rows":
        numeric_columns = list(cleaned.select_dtypes(include="number").columns)
        if numeric_columns:
            cleaned = cleaned.dropna(subset=numeric_columns)
    elif numeric_strategy in {"mean", "median"}:
        for column in cleaned.select_dtypes(include="number").columns:
            values = cleaned[column]
            if values.isna().any() and values.notna().any():
                fill_value = values.mean() if numeric_strategy == "mean" else values.median()
                cleaned[column] = values.fillna(fill_value)

    if categorical_strategy == "drop rows":
        columns = list(cleaned.select_dtypes(exclude="number").columns)
        if columns:
            cleaned = cleaned.dropna(subset=columns)
    elif categorical_strategy == "fill with 'Unknown'":
        for column in cleaned.select_dtypes(exclude="number").columns:
            cleaned[column] = cleaned[column].fillna("Unknown")
    elif categorical_strategy == "most common value":
        for column in cleaned.select_dtypes(exclude="number").columns:
            modes = cleaned[column].mode(dropna=True)
            if cleaned[column].isna().any() and not modes.empty:
                cleaned[column] = cleaned[column].fillna(modes.iloc[0])

    return cleaned.reset_index(drop=True)
