#!/usr/bin/env python3
"""Upload test data files to cloud storage (S3 or ADLS Gen2).

Detects target from environment variables:
- CLOUD_PROVIDER=aws + S3_BUCKET → uploads via boto3
- CLOUD_PROVIDER=azure + STORAGE_ACCOUNT + STORAGE_CONTAINER → uploads via azure SDK
"""

import os
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


def upload_to_s3(bucket: str) -> None:
    """Upload all files in DATA_DIR to an S3 bucket."""
    import boto3

    s3 = boto3.client("s3")
    for fpath in DATA_DIR.iterdir():
        if fpath.is_file():
            key = f"test-data/{fpath.name}"
            print(f"  Uploading {fpath.name} → s3://{bucket}/{key}")
            s3.upload_file(str(fpath), bucket, key)
    print("S3 upload complete.")


def upload_to_adls(account: str, container: str) -> None:
    """Upload all files in DATA_DIR to ADLS Gen2."""
    from azure.identity import DefaultAzureCredential
    from azure.storage.filedatalake import DataLakeServiceClient

    credential = DefaultAzureCredential()
    service = DataLakeServiceClient(
        account_url=f"https://{account}.dfs.core.windows.net",
        credential=credential,
    )
    fs = service.get_file_system_client(container)

    for fpath in DATA_DIR.iterdir():
        if fpath.is_file():
            remote = f"test-data/{fpath.name}"
            print(f"  Uploading {fpath.name} → adls://{container}/{remote}")
            fc = fs.get_file_client(remote)
            with open(fpath, "rb") as f:
                fc.upload_data(f, overwrite=True)
    print("ADLS upload complete.")


def main() -> None:
    """Detect cloud provider and upload test data."""
    provider = os.environ.get("CLOUD_PROVIDER", "").lower()

    if provider == "aws":
        bucket = os.environ.get("S3_BUCKET")
        if not bucket:
            print("Error: S3_BUCKET env var required for AWS uploads")
            sys.exit(1)
        upload_to_s3(bucket)
    elif provider == "azure":
        account = os.environ.get("STORAGE_ACCOUNT")
        container = os.environ.get("STORAGE_CONTAINER", "dataquality")
        if not account:
            print("Error: STORAGE_ACCOUNT env var required for Azure uploads")
            sys.exit(1)
        upload_to_adls(account, container)
    else:
        print("Error: Set CLOUD_PROVIDER=aws or CLOUD_PROVIDER=azure")
        sys.exit(1)


if __name__ == "__main__":
    main()
