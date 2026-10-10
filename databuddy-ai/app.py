from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from modules.ai_provider import answer_with_bedrock, is_bedrock_configured
from modules.chat_assistant import answer_question
from modules.data_analysis import (
    dataset_metrics,
    numeric_correlations,
    quality_report,
    simple_explanation,
    statistical_summary,
)
from modules.data_cleaning import CATEGORICAL_STRATEGIES, NUMERIC_STRATEGIES, clean_dataset
from modules.data_loader import DataLoadError, load_csv_bytes
from modules.visualization import CHART_TYPES, build_chart

st.set_page_config(
    page_title="DataBuddy AI | Friendly data analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(
    """
    <style>
    :root {
      --db-ink: #172f51;
      --db-muted: #63748b;
      --db-blue: #2676e8;
      --db-sky: #eef6ff;
      --db-line: #e1eaf5;
      --db-surface: #ffffff;
    }
    .stApp { background: linear-gradient(145deg, #f7fbff 0%, #ffffff 42%, #f2f8ff 100%); }
    h1, h2, h3 { color: var(--db-ink); letter-spacing: -0.025em; }
    .block-container { max-width: 1420px; padding-top: 2rem; }
    [data-testid="stSidebar"] { background: #f7fbff; border-right: 1px solid var(--db-line); }
    .db-eyebrow { color: #2676e8; font-size: .77rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
    .db-hero {
      background: radial-gradient(circle at 85% 8%, rgba(78, 158, 255, .2), transparent 28%),
                  linear-gradient(120deg, #ffffff, #eef6ff);
      border: 1px solid #dce9f8; border-radius: 22px; padding: 2rem 2.2rem;
      box-shadow: 0 14px 42px rgba(46, 95, 153, .08); margin: .4rem 0 1.35rem;
    }
    .db-hero p { color: var(--db-muted); font-size: 1.05rem; max-width: 760px; line-height: 1.6; }
    .db-card {
      background: var(--db-surface); border: 1px solid var(--db-line); border-radius: 18px;
      padding: 1rem 1.15rem; box-shadow: 0 8px 24px rgba(39, 80, 125, .055);
    }
    .db-note { color: var(--db-muted); font-size: .9rem; }
    div[data-testid="stMetric"] {
      background: white; border: 1px solid var(--db-line); border-radius: 16px;
      padding: .9rem 1rem; box-shadow: 0 7px 22px rgba(39, 80, 125, .045);
    }
    div[data-testid="stMetricLabel"] { color: var(--db-muted); }
    div.stButton > button[kind="primary"] {
      background: linear-gradient(105deg, #2676e8, #4899f5); border: 0; border-radius: 11px;
      box-shadow: 0 7px 18px rgba(38, 118, 232, .2);
    }
    div.stButton > button { border-radius: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid var(--db-line); }
    .stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: .65rem 1rem; }
    .db-footer { color: #8492a6; font-size: .82rem; padding-top: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_state() -> None:
    defaults = {
        "source_df": None,
        "working_df": None,
        "dataset_label": None,
        "simple_explanation": None,
        "chat_history": [],
        "last_upload_signature": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_dataset(frame: pd.DataFrame, label: str) -> None:
    st.session_state.source_df = frame.copy(deep=True)
    st.session_state.working_df = frame.copy(deep=True)
    st.session_state.dataset_label = label
    st.session_state.simple_explanation = None
    st.session_state.chat_history = []


def describe_chart_help(chart_type: str) -> str:
    descriptions = {
        "Histogram": "See how often numeric values fall into different ranges.",
        "Bar chart": "Compare how many rows contain each value.",
        "Line chart": "Follow a numeric value across an ordered column.",
        "Scatter plot": "Look for a relationship between two numeric columns.",
        "Box plot": "Compare the spread and typical range of numeric values.",
        "Correlation heatmap": "Compare how pairs of numeric columns move together.",
    }
    return descriptions[chart_type]


initialize_state()

with st.sidebar:
    st.markdown("## DataBuddy AI 🤖")
    st.caption("Your friendly companion for smarter data analysis.")
    st.markdown("---")
    st.markdown("### Your dataset")
    uploaded = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        max_upload_size=25,
        help="Files are analyzed in memory and are not saved by this app. Maximum size: 25 MB.",
    )
    use_sample = st.button("Use sample dataset", use_container_width=True)
    if use_sample:
        sample_path = APP_DIR / "sample_data" / "student_performance.csv"
        try:
            sample_frame = pd.read_csv(sample_path)
            set_dataset(sample_frame, "Student performance sample")
            st.session_state.last_upload_signature = None
            st.success("Sample dataset loaded.")
        except (OSError, pd.errors.ParserError) as error:
            st.error(f"The sample dataset could not be opened: {error}")

    if uploaded is not None:
        signature = (uploaded.name, uploaded.size, getattr(uploaded, "file_id", None))
        if signature != st.session_state.last_upload_signature:
            try:
                frame = load_csv_bytes(uploaded.getvalue(), uploaded.name)
                set_dataset(frame, uploaded.name)
                st.session_state.last_upload_signature = signature
                st.success(f"Loaded {uploaded.name}.")
            except DataLoadError as error:
                st.session_state.last_upload_signature = signature
                st.error(str(error))

    current_df = st.session_state.working_df
    if current_df is not None:
        st.markdown("---")
        st.markdown("**Current file**")
        st.caption(st.session_state.dataset_label)
        st.caption(f"{len(current_df):,} rows · {len(current_df.columns):,} columns")
        st.info("The original upload stays unchanged. Cleaning is applied only to a separate working copy.")
    st.markdown("---")
    selected_section = st.radio(
        "Navigate",
        ["Overview", "Visualize", "Clean data", "Ask DataBuddy"],
        label_visibility="visible",
    )
    st.caption("Local mode is ready. No AWS account or API key is needed.")

st.markdown(
    """
    <div class="db-hero">
      <div class="db-eyebrow">Your personal data analyst</div>
      <h1 style="margin: .35rem 0 .4rem;">DataBuddy AI <span aria-hidden="true">🤖</span></h1>
      <p>Your friendly companion for smarter data analysis. Upload a CSV or explore the sample, then ask questions and find patterns in plain English.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

frame = st.session_state.working_df
if frame is None:
    welcome_left, welcome_right = st.columns([1.35, 1])
    with welcome_left:
        st.subheader("Start with a dataset")
        st.write(
            "Explore a file without writing code. DataBuddy checks its quality, makes interactive charts, "
            "and helps explain the results in everyday language."
        )
        st.info("Choose **Use sample dataset** in the sidebar to try the app now, or upload your own CSV.")
        st.markdown("**Try asking:**")
        for prompt in (
            "How many missing values are there?",
            "Which column has the highest average?",
            "What should I do next?",
        ):
            st.markdown(f"- “{prompt}”")
    with welcome_right:
        st.markdown(
            """
            <div class="db-card">
              <div class="db-eyebrow">Privacy by default</div>
              <h3>Made for curious learners</h3>
              <p class="db-note">Your CSV stays in this app session. It is not stored permanently or sent to AWS. The built-in assistant uses computed dataset facts and works offline.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.stop()

metrics = dataset_metrics(frame)
if selected_section == "Overview":
    st.subheader("Your data at a glance")
    st.caption(f"Currently analyzing **{st.session_state.dataset_label}**.")
    metric_columns = st.columns(4)
    metric_columns[0].metric("Rows", f"{metrics['rows']:,}")
    metric_columns[1].metric("Columns", f"{metrics['columns']:,}")
    metric_columns[2].metric("Missing cells", f"{metrics['missing_cells']:,}")
    metric_columns[3].metric("Duplicate rows", f"{metrics['duplicate_rows']:,}")

    quality = quality_report(frame)
    st.markdown("### Data quality report")
    st.caption("A missing value is an empty cell. Unique values count how many different non-empty values a column contains.")
    st.dataframe(quality, use_container_width=True, hide_index=True)

    with st.expander("Preview the first 100 rows"):
        st.dataframe(frame.head(100), use_container_width=True, hide_index=True)
        st.caption(f"Showing {min(100, len(frame)):,} of {len(frame):,} rows.")

    st.markdown("### Explain my data simply")
    st.write("Get a short summary, quality notes, numeric observations, chart ideas, and three next steps.")
    if st.button("Explain My Data Simply", type="primary", key="explain_data"):
        st.session_state.simple_explanation = simple_explanation(frame)
    explanation = st.session_state.simple_explanation
    if explanation:
        st.markdown(f"**In short:** {explanation['summary']}")
        detail_left, detail_right = st.columns(2)
        with detail_left:
            st.markdown("**Things to check**")
            for issue in explanation["quality_issues"]:
                st.markdown(f"- {issue}")
            st.markdown("**Useful visualizations**")
            for suggestion in explanation["visualizations"]:
                st.markdown(f"- {suggestion}")
        with detail_right:
            st.markdown("**What stands out**")
            for observation in explanation["observations"]:
                st.markdown(f"- {observation}")
            st.markdown("**Three next steps**")
            for number, step in enumerate(explanation["next_steps"], start=1):
                st.markdown(f"{number}. {step}")

    st.markdown("### Download reports")
    summary = statistical_summary(frame)
    download_cols = st.columns(3)
    download_cols[0].download_button(
        "Download statistical summary",
        data=summary.to_csv(index=False).encode("utf-8"),
        file_name="databuddy_statistical_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )
    download_cols[1].download_button(
        "Download data quality report",
        data=quality.to_csv(index=False).encode("utf-8"),
        file_name="databuddy_data_quality.csv",
        mime="text/csv",
        use_container_width=True,
    )
    download_cols[2].download_button(
        "Download working dataset",
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name="databuddy_cleaned_data.csv",
        mime="text/csv",
        use_container_width=True,
    )

elif selected_section == "Visualize":
    st.subheader("Explore a pattern")
    st.write("Pick a chart. DataBuddy will let you know if a chart does not fit the selected columns.")
    chart_type = st.selectbox("Chart type", CHART_TYPES, key="chart_type")
    st.caption(describe_chart_help(chart_type))
    numeric_columns = list(frame.select_dtypes(include="number").columns)

    if chart_type == "Correlation heatmap":
        correlation = numeric_correlations(frame)
        if correlation.empty:
            st.info("A correlation heatmap needs at least two numeric columns.")
        else:
            try:
                chart = build_chart(frame, chart_type)
                st.plotly_chart(chart, use_container_width=True)
            except ValueError as error:
                st.warning(str(error))
    else:
        column_options = list(frame.columns)
        controls = st.columns(2)
        x_column = controls[0].selectbox("Column", column_options, key="chart_x")
        y_column = None
        if chart_type in {"Line chart", "Scatter plot"}:
            y_options = [column for column in numeric_columns if column != x_column]
            if not y_options:
                st.info(f"A {chart_type.lower()} needs another numeric column.")
            else:
                y_column = controls[1].selectbox("Numeric value", y_options, key="chart_y")
        try:
            if chart_type in {"Line chart", "Scatter plot"} and y_column is None:
                raise ValueError(f"A {chart_type.lower()} needs a second numeric column.")
            chart = build_chart(frame, chart_type, x_column, y_column)
            st.plotly_chart(chart, use_container_width=True)
        except ValueError as error:
            st.warning(str(error))

elif selected_section == "Clean data":
    st.subheader("Clean a working copy")
    st.write("Preview a proposed change before applying it. Your original uploaded or sample data is kept separately.")
    source_df = st.session_state.source_df
    original_metrics = dataset_metrics(source_df)
    st.caption(
        f"Original: {original_metrics['rows']:,} rows · {original_metrics['missing_cells']:,} missing cells · "
        f"{original_metrics['duplicate_rows']:,} duplicate rows"
    )

    clean_options_left, clean_options_right = st.columns(2)
    with clean_options_left:
        remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
        numeric_strategy = st.selectbox("Numeric missing values", NUMERIC_STRATEGIES, index=0)
    with clean_options_right:
        categorical_strategy = st.selectbox(
            "Category or text missing values", CATEGORICAL_STRATEGIES, index=0
        )
        st.caption(
            "Mean uses the average; median uses the middle value. The most common value fills text blanks."
        )

    preview_df = clean_dataset(
        source_df,
        remove_duplicates=remove_duplicates,
        numeric_strategy=numeric_strategy,
        categorical_strategy=categorical_strategy,
    )
    preview_metrics = dataset_metrics(preview_df)
    preview_cols = st.columns(4)
    preview_cols[0].metric("Rows after change", f"{preview_metrics['rows']:,}")
    preview_cols[1].metric("Rows removed", f"{max(0, original_metrics['rows'] - preview_metrics['rows']):,}")
    preview_cols[2].metric("Missing cells left", f"{preview_metrics['missing_cells']:,}")
    preview_cols[3].metric("Duplicate rows left", f"{preview_metrics['duplicate_rows']:,}")
    st.markdown("**Preview the proposed data**")
    st.dataframe(preview_df.head(100), use_container_width=True, hide_index=True)
    with st.expander("Compare original and proposed quality"):
        comparison = quality_report(source_df).merge(
            quality_report(preview_df),
            on="column",
            how="outer",
            suffixes=("_original", "_proposed"),
        )
        compare_columns = [
            column
            for column in (
                "column",
                "missing_count_original",
                "missing_count_proposed",
                "unique_values_original",
                "unique_values_proposed",
            )
            if column in comparison.columns
        ]
        st.dataframe(comparison[compare_columns], use_container_width=True, hide_index=True)

    if st.button("Apply these changes to my working copy", type="primary"):
        set_dataset(source_df, st.session_state.dataset_label)
        st.session_state.working_df = preview_df.copy(deep=True)
        st.session_state.simple_explanation = None
        st.success("Changes applied to the working copy. The original data is still preserved.")

    st.download_button(
        "Download proposed cleaned CSV",
        data=preview_df.to_csv(index=False).encode("utf-8"),
        file_name="databuddy_cleaned_data.csv",
        mime="text/csv",
        use_container_width=True,
    )

elif selected_section == "Ask DataBuddy":
    st.subheader("Ask DataBuddy")
    st.write("The local assistant answers supported questions with values calculated from your current working data.")
    if is_bedrock_configured():
        st.success("Optional Bedrock settings are present. Questions may use the configured model.")
    else:
        st.info(
            "Local assistant is active. No generative AI model is connected; answers below come from "
            "Python calculations, not invented dataset values."
        )
    with st.expander("Questions DataBuddy supports"):
        for question in (
            "Explain this dataset in simple English.",
            "How many missing values are there?",
            "Which column has the highest average?",
            "Show me the correlation between numerical columns.",
            "Are there any duplicate records?",
            "What insights can I find in this dataset?",
            "Which chart should I use?",
            "What should I do next?",
        ):
            st.markdown(f"- {question}")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask about the data in this file…")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Checking the dataset…"):
                try:
                    facts = simple_explanation(frame)
                    bedrock_answer = answer_with_bedrock(question, facts) if is_bedrock_configured() else None
                    response = bedrock_answer or answer_question(question, frame)
                except Exception as error:  # surfaced clearly; local assistant remains deterministic
                    st.warning(f"Bedrock could not answer this request, so I used the local assistant: {error}")
                    response = answer_question(question, frame)
                st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

st.markdown(
    '<div class="db-footer">DataBuddy AI · Local-first by design · Your original dataset is never overwritten.</div>',
    unsafe_allow_html=True,
)
