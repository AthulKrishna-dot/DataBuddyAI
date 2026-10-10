"""Reliable, deterministic question answering for the local MVP."""

from __future__ import annotations

import pandas as pd

from modules.data_analysis import dataset_metrics, simple_explanation

SUPPORTED_QUESTIONS = (
    "Explain this dataset in simple English",
    "How many missing values are there?",
    "Which column has the highest average?",
    "Show me the correlation between numerical columns",
    "Are there any duplicate records?",
    "What insights can I find in this dataset?",
    "Which chart should I use?",
    "What should I do next?",
)


def answer_question(question: str, frame: pd.DataFrame) -> str:
    """Answer supported dataset questions with computed values only."""
    text = question.strip().lower()
    if not text:
        return "Type a question about your dataset to get started."

    if any(word in text for word in ("missing", "blank", "empty cell")):
        missing = frame.isna().sum()
        total = int(missing.sum())
        if total == 0:
            return f"There are no missing cells in this dataset ({len(frame):,} rows checked)."
        top = missing[missing > 0].sort_values(ascending=False)
        details = ", ".join(f"{column}: {int(count)}" for column, count in top.items())
        return f"There are {total:,} missing cells. By column: {details}."

    if any(word in text for word in ("duplicate", "repeated row", "copies")):
        count = int(frame.duplicated().sum())
        if count:
            return f"I found {count:,} duplicate rows. The original data has not been changed."
        return "I found no duplicate rows."

    if any(word in text for word in ("highest average", "highest mean", "largest average", "average")):
        numeric = frame.select_dtypes(include="number")
        means = numeric.mean().dropna()
        if means.empty:
            return "There are no numeric columns with values to average."
        column = str(means.idxmax())
        return f"{column} has the highest average: {means.max():,.2f}."

    if "correlation" in text or "correlat" in text:
        numeric = frame.select_dtypes(include="number")
        if numeric.shape[1] < 2:
            return "A correlation compares two numeric columns. This dataset needs at least two."
        matrix = numeric.corr()
        pairs: list[tuple[float, str, str]] = []
        for left_index, left in enumerate(matrix.columns):
            for right in matrix.columns[left_index + 1 :]:
                value = matrix.loc[left, right]
                if pd.notna(value):
                    pairs.append((abs(float(value)), str(left), str(right)))
        if not pairs:
            return "I couldn't calculate a correlation because the numeric columns have too few usable values."
        strongest = sorted(pairs, reverse=True)[:5]
        relationships: list[str] = []
        for _, left, right in strongest:
            signed = float(matrix.loc[left, right])
            direction = "move in the same direction" if signed >= 0 else "often move in opposite directions"
            relationships.append(f"{left} and {right}: {signed:.2f} ({direction})")
        return (
            "The strongest numeric relationships are: "
            + "; ".join(relationships)
            + ". Correlation shows a pattern, not proof of cause."
        )

    if any(word in text for word in ("chart", "visual", "plot", "graph")):
        numeric = list(frame.select_dtypes(include="number").columns)
        other = list(frame.select_dtypes(exclude="number").columns)
        ideas: list[str] = []
        if numeric:
            ideas.append(f"a histogram for {numeric[0]}")
        if other:
            ideas.append(f"a bar chart for {other[0]}")
        if len(numeric) >= 2:
            ideas.append("a scatter plot or correlation heatmap for numeric relationships")
        if not ideas:
            return "A bar chart is a good first choice for counting values in a category column."
        return "A good place to start is " + ", ".join(ideas) + "."

    if any(word in text for word in ("next", "recommend", "do now", "what should i do")):
        explanation = simple_explanation(frame)
        return "Here are three useful next steps:\n" + "\n".join(
            f"{index}. {step}" for index, step in enumerate(explanation["next_steps"], start=1)
        )

    if any(word in text for word in ("insight", "explain", "describe", "dataset", "data in simple")):
        explanation = simple_explanation(frame)
        observations = " ".join(explanation["observations"])
        issues = " ".join(explanation["quality_issues"])
        return f"{explanation['summary']} {issues} {observations}"

    metrics = dataset_metrics(frame)
    return (
        "I can answer questions about the dataset's size, missing values, duplicates, averages, "
        "numeric correlations, chart choices, insights, and next steps. "
        f"This dataset currently has {metrics['rows']:,} rows and {metrics['columns']:,} columns."
    )
