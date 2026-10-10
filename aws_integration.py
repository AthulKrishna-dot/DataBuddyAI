import os
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BUCKET = os.getenv("AWS_BUCKET")


def get_s3_client():
    if not AWS_BUCKET:
        raise ValueError(
            "AWS_BUCKET is not set. Add it to your environment or .env file before uploading files."
        )
    return boto3.client("s3", region_name=AWS_REGION)


def upload_demo_file(local_path: str = "sample_data.csv", key: str = "demo/sample_data.csv") -> str:
    """Upload a file to S3 and return its public S3 URI when configured."""
    client = get_s3_client()
    try:
        client.upload_file(local_path, AWS_BUCKET, key)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Unable to upload to S3: {exc}") from exc

    return f"s3://{AWS_BUCKET}/{key}"


def list_bucket_objects(prefix: str = "") -> list[str]:
    """List objects in the configured bucket for a given prefix."""
    client = get_s3_client()
    paginator = client.get_paginator("list_objects_v2")
    keys: list[str] = []

    try:
        for page in paginator.paginate(Bucket=AWS_BUCKET, Prefix=prefix):
            for item in page.get("Contents", []):
                keys.append(item["Key"])
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Unable to list S3 objects: {exc}") from exc

    return keys


def download_object(key: str, destination: str | None = None) -> str:
    """Download an S3 object to a local file path."""
    client = get_s3_client()
    target = destination or Path(key).name
    try:
        client.download_file(AWS_BUCKET, key, target)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Unable to download S3 object: {exc}") from exc

    return target
