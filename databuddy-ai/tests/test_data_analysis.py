import pandas as pd
import pytest

from modules.data_analysis import (
    dataset_metrics,
    numeric_correlations,
    quality_report,
    simple_explanation,
    statistical_summary,
)
from modules.data_loader import DataLoadError, load_csv_bytes


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "hours": [1.0, 2.0, 3.0, 3.0],
            "score": [50.0, 70.0, 80.0, 80.0],
            "group": ["A", "B", None, None],
        }
    )


def test_valid_csv_upload_and_preview_shape():
    frame = load_csv_bytes(b"score,name\n82,Ada\n91,Sam\n", "students.csv")
    assert frame.shape == (2, 2)
    assert frame.loc[0, "name"] == "Ada"


@pytest.mark.parametrize("payload", [b"", b"   ", b",\n,\n"])
def test_empty_csv_is_rejected(payload):
    with pytest.raises(DataLoadError):
        load_csv_bytes(payload)


def test_malformed_csv_is_rejected():
    with pytest.raises(DataLoadError):
        load_csv_bytes(b"name,score\nAda,90\nSam,80,extra\n")


def test_wrong_extension_and_oversized_upload_are_rejected():
    with pytest.raises(DataLoadError, match="\\.csv"):
        load_csv_bytes(b"a,b\n1,2", "data.txt")
    with pytest.raises(DataLoadError, match="upload limit"):
        load_csv_bytes(b"a\n123", max_bytes=2)


def test_metrics_quality_and_numeric_statistics():
    frame = sample_frame()
    metrics = dataset_metrics(frame)
    assert metrics == {"rows": 4, "columns": 3, "missing_cells": 2, "duplicate_rows": 1}
    report = quality_report(frame).set_index("column")
    assert report.loc["group", "missing_count"] == 2
    assert report.loc["group", "missing_percent"] == 50.0
    assert report.loc["hours", "unique_values"] == 3
    assert "mean" in report.loc["hours", "basic_summary"]
    assert "score" in statistical_summary(frame)["column"].tolist()


def test_correlation_calculates_numeric_relationships():
    correlation = numeric_correlations(sample_frame())
    assert correlation.loc["hours", "score"] == pytest.approx(0.98473, abs=0.001)


def test_explanation_uses_actual_counts():
    explanation = simple_explanation(sample_frame())
    assert "4 rows" in explanation["summary"]
    assert "2 missing cells" in explanation["summary"]
    assert len(explanation["next_steps"]) == 3
