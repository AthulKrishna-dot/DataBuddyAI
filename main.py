import os

from aws_integration import upload_demo_file


def main():
    bucket = os.getenv("AWS_BUCKET")
    if not bucket:
        print("AWS integration is ready.")
        print("Set AWS_BUCKET and AWS_REGION in your environment or .env file.")
        print("Example: export AWS_BUCKET=data-buddy-ai-demo")
        return

    try:
        location = upload_demo_file("sample_data.csv", "demo/sample_data.csv")
        print(f"File uploaded successfully to {location}")
    except Exception as exc:
        print(f"AWS upload failed: {exc}")
        print("Check your AWS credentials, bucket permissions, and bucket name.")


if __name__ == "__main__":
    main()
