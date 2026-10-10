from io import BytesIO

import pandas as pd

from modules.chat_assistant import answer_question


def test_supported_chat_answers_are_grounded_in_values():
    frame = pd.DataFrame(
        {
            "study_hours": [1.0, 3.0, 5.0],
            "score": [40.0, 60.0, 90.0],
            "team": ["A", "A", None],
        }
    )
    assert "1 missing cells" in answer_question("How many missing values?", frame)
    assert "score" in answer_question("Which column has the highest average?", frame)
    assert "no duplicate rows" in answer_question("Any duplicate records?", frame)
    assert "correlation" in answer_question("Show correlations", frame).lower()


def test_unsupported_chat_is_explicit_and_suggests_supported_topics():
    answer = answer_question("What is the weather tomorrow?", pd.DataFrame({"x": [1]}))
    assert "I can answer questions" in answer
    assert "averages" in answer


def test_cleaned_csv_export_can_be_serialized():
    frame = pd.DataFrame({"score": [10, 20], "label": ["A", "B"]})
    exported = frame.to_csv(index=False).encode("utf-8")
    restored = pd.read_csv(BytesIO(exported))
    pd.testing.assert_frame_equal(restored, frame)
