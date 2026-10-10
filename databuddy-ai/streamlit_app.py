"""Stable Streamlit entry point for DataBuddy AI."""

from pathlib import Path
import runpy


APP_PATH = Path(__file__).resolve().with_name("app.py")
runpy.run_path(str(APP_PATH), run_name="__main__")
