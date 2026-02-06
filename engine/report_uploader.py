"""Upload HTML reports to cloud storage or save locally."""

from pathlib import Path


def upload_report_to_s3(html: str, bucket: str, key: str) -> str:
    """Upload HTML report to S3, return public URL.

    Args:
        html: HTML content string.
        bucket: S3 bucket name.
        key: S3 object key.

    Returns:
        Public URL of the uploaded report.
    """
    import boto3

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=html.encode("utf-8"),
        ContentType="text/html",
    )
    return f"https://{bucket}.s3.amazonaws.com/{key}"


def upload_report_to_azure_blob(
    html: str, account: str, container: str, blob_name: str
) -> str:
    """Upload HTML report to Azure Blob Storage, return URL.

    Args:
        html: HTML content string.
        account: Azure storage account name.
        container: Blob container name.
        blob_name: Blob name/path.

    Returns:
        Public URL of the uploaded report.
    """
    from azure.storage.blob import BlobServiceClient

    url = f"https://{account}.blob.core.windows.net"
    client = BlobServiceClient(account_url=url)
    blob_client = client.get_container_client(container).get_blob_client(blob_name)
    blob_client.upload_blob(
        html.encode("utf-8"),
        content_type="text/html",
        overwrite=True,
    )
    return f"{url}/{container}/{blob_name}"


def save_report_local(html: str, path: str) -> str:
    """Save report locally, return file path.

    Args:
        html: HTML content string.
        path: Local file path.

    Returns:
        Absolute path to the saved file.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")
    return str(p.resolve())
