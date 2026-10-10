# DataBuddyAI AWS Integration

This repository includes a lightweight AWS free-tier integration layer for common storage and data-workflow use cases.

## Free AWS services suitable for this project

- S3: store CSV/JSON exports and uploaded files
- Lambda: run small ETL jobs and serverless processors
- DynamoDB: store metadata or small app state
- CloudWatch: monitor logs and metrics
- EC2: host the backend for non-trivial workloads
- RDS: managed PostgreSQL for relational data

## Local setup

1. Install dependencies:
   ```bash
   python -m pip install -U pip
   python -m pip install -e .
   ```

2. Copy the example env file:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your AWS credentials and bucket name:
   ```bash
   AWS_REGION=us-east-1
   AWS_BUCKET=my-data-buddy-bucket
   ```

4. Configure AWS credentials using the AWS CLI:
   ```bash
   aws configure
   ```

## Example usage

```bash
python main.py
```

The script will upload `sample_data.csv` to your configured S3 bucket.

## Files added

- `aws_integration.py` — AWS S3 helpers for upload/list/download
- `sample_data.csv` — sample dataset
- `.env.example` — sample environment configuration
