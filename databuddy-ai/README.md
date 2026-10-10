# DataBuddy AI

DataBuddy AI is a local-first data analytics assistant for students and beginners. Upload a CSV, explore its quality and patterns, clean a separate working copy, and ask questions in plain English. Uploaded files are analyzed in memory and are not saved by the app.

## Features

- CSV upload with a 25 MB limit, validation, and a preview of up to 100 rows.
- Overview counts and a column-by-column quality report.
- Interactive Plotly histograms, bar charts, line charts, scatter plots, box plots, and correlation heatmaps.
- Non-destructive cleaning preview for duplicate rows and missing values.
- A deterministic local chat assistant that only reports values computed from the dataset.
- “Explain My Data Simply” summaries, three next steps, and suggested charts.
- Downloads for cleaned CSV, statistical summary CSV, and data quality CSV.
- Optional, modular Amazon Bedrock support. The app runs without AWS settings or credentials.

## Technology

Python, Streamlit, pandas, NumPy, Plotly, and pytest. The optional Bedrock adapter uses boto3 only when explicitly configured. Amazon S3 and AWS Lambda are future extension points; the local app does not upload data or provision AWS resources.

## Project structure

```text
databuddy-ai/
├── app.py
├── requirements.txt
├── README.md
├── modules/
│   ├── ai_provider.py
│   ├── chat_assistant.py
│   ├── data_analysis.py
│   ├── data_cleaning.py
│   ├── data_loader.py
│   └── visualization.py
├── sample_data/student_performance.csv
└── tests/
```

## Run locally

Python 3.10 or newer is recommended.

```bash
cd databuddy-ai
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL when the server starts. Choose **Use sample dataset** to explore without uploading a file.

## Run tests

From this directory:

```bash
python -m pytest -q
```

Expected result: all tests pass, covering valid and invalid CSV uploads, size/extension checks, missing and duplicate counts, numerical summaries, correlations, cleaning and preservation of the original frame, CSV export, and unsupported chat questions.

## Optional Amazon Bedrock

The local Python assistant remains available if Bedrock is not configured. To enable the optional provider, install boto3 (`pip install boto3`) and set AWS configuration through your normal AWS credentials provider and environment:

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=your-enabled-bedrock-model-id
```

Credentials must not be placed in source code or committed files. Bedrock calls are made only when a model ID and region are configured. Access must be enabled for the selected model in the AWS account. The provider sends the question and computed dataset facts to Bedrock for an explanation; it does not send the full dataset. No S3 storage or Lambda resources are created by this project.

## Limitations and next steps

- Local chat supports dataset summaries, missing values, duplicates, numeric averages, correlations, chart suggestions, and next steps; unrelated questions are explicitly marked unsupported.
- Bedrock supports the optional Claude Messages request format; adapt `modules/ai_provider.py` if a different model family is selected.
- S3 consent and retention controls, Lambda deployment, and multi-user storage are not implemented.
- For screenshots, run the app with the sample dataset, capture the Overview and Visualize pages from your browser, and label them as screenshots of the running app.
- Future AWS work should add explicit per-upload consent, scoped IAM permissions, retention rules, and a cost review before creating cloud resources.

## Sample data

`sample_data/student_performance.csv` includes a missing study-hours value, a missing attendance value, and one intentionally duplicated student row so the quality and cleaning tools can be exercised immediately.
