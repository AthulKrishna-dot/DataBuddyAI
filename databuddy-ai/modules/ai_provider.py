"""Optional Amazon Bedrock provider; local analysis never depends on it."""

from __future__ import annotations

import json
import os
from typing import Any


def is_bedrock_configured() -> bool:
    """Return whether a model ID and AWS region were explicitly configured."""
    return bool(os.getenv("BEDROCK_MODEL_ID") and (os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")))


def answer_with_bedrock(question: str, computed_facts: dict[str, Any]) -> str | None:
    """Ask a configured Bedrock model to explain supplied facts, or return None locally."""
    if not is_bedrock_configured():
        return None

    try:
        import boto3
    except ImportError as error:
        raise RuntimeError(
            "Bedrock settings are present, but the optional boto3 package is not installed. "
            "Install the AWS extras described in the README."
        ) from error

    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    model_id = os.environ["BEDROCK_MODEL_ID"]
    client = boto3.client("bedrock-runtime", region_name=region)
    prompt = (
        "Answer the user's question for a beginner using only the computed dataset facts below. "
        "If the facts do not answer the question, say so. Do not invent numbers, columns, or causes.\n\n"
        f"Computed facts: {json.dumps(computed_facts, ensure_ascii=False, default=str)}\n\n"
        f"Question: {question}"
    )
    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            }
        ),
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    content = payload.get("content", [])
    return "\n".join(item.get("text", "") for item in content if item.get("type") == "text").strip()
