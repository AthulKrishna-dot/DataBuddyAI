import pandas as pd
import pytest

from modules.data_cleaning import clean_dataset


def test_cleaning_returns_copy_and_fills_numeric_and_category_values():
    original = pd.DataFrame(
        {"score": [10.0, None, 30.0, 30.0], "group": ["A", None, "B", "B"]}
    )
    cleaned = clean_dataset(
        original,
        remove_duplicates=True,
        numeric_strategy="mean",
        categorical_strategy="most common value",
    )
    assert original["score"].isna().sum() == 1
    assert cleaned["score"].isna().sum() == 0
    assert cleaned["group"].isna().sum() == 0
    assert len(cleaned) == 3
    assert cleaned is not original


def test_drop_rows_strategies_and_leave_unchanged():
    original = pd.DataFrame({"score": [10.0, None], "label": ["A", None]})
    assert len(clean_dataset(original, numeric_strategy="drop rows")) == 1
    assert len(clean_dataset(original, categorical_strategy="drop rows")) == 1
    unchanged = clean_dataset(
        original,
        remove_duplicates=False,
        numeric_strategy="leave unchanged",
        categorical_strategy="leave unchanged",
    )
    assert unchanged.isna().sum().sum() == 2


def test_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="numeric strategy"):
        clean_dataset(pd.DataFrame({"score": [1]}), numeric_strategy="guess")
