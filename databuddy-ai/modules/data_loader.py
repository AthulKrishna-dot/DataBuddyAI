"""Safe, in-memory CSV loading helpers."""

from __future__ import annotations

from io import BytesIO

import pandas as pd

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


class DataLoadError(ValueError):
    """Raised when an uploaded CSV cannot be safely analyzed."""


def load_csv_bytes(
    content: bytes,
    filename: str = "upload.csv",
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> pd.DataFrame:
    """Load a CSV from bytes without writing it to disk."""
    if not filename.lower().endswith(".csv"):
        raise DataLoadError("Please choose a file with a .csv extension.")
    if not content:
        raise DataLoadError("This file is empty. Choose a CSV that contains a header and data.")
    if len(content) > max_bytes:
        limit_mb = max_bytes // (1024 * 1024)
        raise DataLoadError(f"This file is larger than the {limit_mb} MB upload limit.")
    if not content.strip():
        raise DataLoadError("This file contains only blank space. Choose a CSV with data.")

    try:
        frame = pd.read_csv(BytesIO(content), encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise DataLoadError(
            "The file is not saved as UTF-8 text. Re-save it as a UTF-8 CSV and try again."
        ) from error
    except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as error:
        raise DataLoadError(
            "I couldn't read this CSV. Check that each row has the same number of fields "
            "and that the first row contains column names."
        ) from error

    if frame.empty and len(frame.columns) == 0:
        raise DataLoadError("This CSV has no columns. Add a header row and try again.")
    if len(frame.columns) == 0:
        raise DataLoadError("This CSV has no columns. Add a header row and try again.")
    if any(not str(column).strip() or str(column).startswith("Unnamed:") for column in frame.columns):
        raise DataLoadError(
            "At least one column is missing a name. Add a name to every column in the header row."
        )
    if frame.shape[1] > 500:
        raise DataLoadError("This file has more than 500 columns, which is above the current limit.")
    if frame.shape[0] > 1_000_000:
        raise DataLoadError("This file has more than 1,000,000 rows, which is above the current limit.")

    return frame
