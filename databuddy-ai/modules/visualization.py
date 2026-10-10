"""Interactive Plotly chart builders."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


CHART_TYPES = ("Histogram", "Bar chart", "Line chart", "Scatter plot", "Box plot", "Correlation heatmap")


def build_chart(
    frame: pd.DataFrame,
    chart_type: str,
    x_column: str | None = None,
    y_column: str | None = None,
) -> go.Figure:
    """Create a validated Plotly chart or raise a useful ValueError."""
    if frame.empty:
        raise ValueError("There are no rows to chart.")
    if chart_type not in CHART_TYPES:
        raise ValueError("Choose one of the available chart types.")

    if chart_type == "Correlation heatmap":
        numeric = frame.select_dtypes(include="number")
        if numeric.shape[1] < 2:
            raise ValueError("A correlation heatmap needs at least two numeric columns.")
        return px.imshow(
            numeric.corr(),
            text_auto=".2f",
            color_continuous_scale="RdBu",
            zmin=-1,
            zmax=1,
            title="How numeric columns move together",
            aspect="auto",
        )

    if x_column not in frame.columns:
        raise ValueError("Choose a column that exists in the dataset.")
    if chart_type in {"Histogram", "Box plot"}:
        if not pd.api.types.is_numeric_dtype(frame[x_column]):
            raise ValueError(f"{chart_type} works best with a numeric column.")
        if chart_type == "Histogram":
            return px.histogram(frame, x=x_column, title=f"How {x_column} is distributed")
        return px.box(frame, y=x_column, points="outliers", title=f"Range of {x_column}")

    if chart_type == "Bar chart":
        counts = frame[x_column].astype("string").fillna("(missing)").value_counts().head(30)
        result = counts.rename_axis(x_column).reset_index(name="rows")
        return px.bar(result, x=x_column, y="rows", title=f"Most common values in {x_column}")

    if y_column not in frame.columns:
        raise ValueError(f"Choose a second column for the {chart_type.lower()}.")
    if not pd.api.types.is_numeric_dtype(frame[y_column]):
        raise ValueError(f"The vertical axis ({y_column}) must be numeric.")
    if chart_type == "Scatter plot" and not pd.api.types.is_numeric_dtype(frame[x_column]):
        raise ValueError("A scatter plot needs numeric columns for both axes.")

    chart_frame = frame[[x_column, y_column]].dropna().copy()
    if chart_frame.empty:
        raise ValueError("These columns do not have any complete pairs of values to chart.")
    if chart_type == "Line chart":
        try:
            chart_frame = chart_frame.sort_values(by=x_column)
        except TypeError:
            pass
        return px.line(chart_frame, x=x_column, y=y_column, markers=True, title=f"{y_column} across {x_column}")
    return px.scatter(chart_frame, x=x_column, y=y_column, title=f"{x_column} compared with {y_column}")
