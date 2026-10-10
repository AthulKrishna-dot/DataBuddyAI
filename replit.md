# DataBuddy AI

DataBuddy AI is a local-first data analytics assistant that helps students and beginners explore CSV datasets in plain English.

## Run & Operate

- Preview workflow: `artifacts/databuddy-ai: web` (runs the Streamlit app through the registered app preview).
- Local run: `cd databuddy-ai && streamlit run app.py`.
- Tests: `cd databuddy-ai && python -m pytest -q`.
- The app does not use the shared API server or database.
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)

## Stack

- App: Python, Streamlit, pandas, NumPy, Plotly
- Optional AI provider: Amazon Bedrock via boto3 when explicitly configured
- Workspace tooling: pnpm, Node.js 24, TypeScript 5.9
- Existing shared API and database artifacts are not used by DataBuddy AI.

## Where things live

- `databuddy-ai/app.py` — Streamlit application and session state
- `databuddy-ai/modules/` — CSV loading, analysis, cleaning, charts, chat, and optional Bedrock adapter
- `databuddy-ai/tests/` — automated Python tests
- `databuddy-ai/sample_data/` — sample CSV with missing values and a duplicate record
- `artifacts/databuddy-ai/run-streamlit.sh` — starts Streamlit under the registered preview service

## Architecture decisions

- Uploaded CSVs are processed in memory and are not persisted.
- Cleaning operates on a separate working copy; the original DataFrame remains unchanged.
- Local chat is deterministic and grounded in computed dataset facts. Bedrock is optional and disabled unless a region and model ID are configured.
- The app does not send datasets to AWS or create AWS resources. Future AWS storage or processing requires explicit user consent and cost confirmation.
- Replit's current static production build is not configured to serve this Streamlit app; keep publishing disabled until Python/Streamlit production serving is configured.

## Product

- Upload CSVs, inspect data quality and statistical summaries, create interactive charts, preview/apply cleaning, ask supported questions, explain the data simply, and download CSV reports.
- Intended for students and beginners; use clear language and explain technical terms.

## User preferences

_No additional preferences recorded._

## Gotchas

- The app upload limit is 25 MB. Keep the uploader limit and CSV loader validation in sync.
- Install optional Bedrock SDK support with `pip install boto3`; AWS credentials must come from an external AWS credentials provider, never source files.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
