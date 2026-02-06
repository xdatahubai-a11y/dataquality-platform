"""Tests for report upload functions (mocked cloud clients)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from engine.report_uploader import save_report_local

SAMPLE_HTML = "<html><body>Test Report</body></html>"


def test_save_report_local(tmp_path: Path) -> None:
    """Test local save creates file with correct content."""
    path = str(tmp_path / "report.html")
    result = save_report_local(SAMPLE_HTML, path)
    assert Path(result).exists()
    assert Path(result).read_text() == SAMPLE_HTML


def test_save_report_local_creates_dirs(tmp_path: Path) -> None:
    """Test local save creates parent directories."""
    path = str(tmp_path / "sub" / "dir" / "report.html")
    result = save_report_local(SAMPLE_HTML, path)
    assert Path(result).exists()


def test_upload_to_s3() -> None:
    """Test S3 upload calls put_object correctly."""
    mock_boto3 = MagicMock()
    with patch.dict(sys.modules, {"boto3": mock_boto3}):
        from engine.report_uploader import upload_report_to_s3

        url = upload_report_to_s3(SAMPLE_HTML, "my-bucket", "reports/test.html")

        mock_boto3.client.return_value.put_object.assert_called_once_with(
            Bucket="my-bucket",
            Key="reports/test.html",
            Body=SAMPLE_HTML.encode("utf-8"),
            ContentType="text/html",
        )
        assert url == "https://my-bucket.s3.amazonaws.com/reports/test.html"


def test_upload_to_azure() -> None:
    """Test Azure Blob upload calls the correct methods."""
    mock_blob_module = MagicMock()
    with patch.dict(sys.modules, {"azure": MagicMock(), "azure.storage": MagicMock(),
                                   "azure.storage.blob": mock_blob_module}):
        from engine.report_uploader import upload_report_to_azure_blob

        url = upload_report_to_azure_blob(SAMPLE_HTML, "myaccount", "reports", "dq.html")

        assert "myaccount" in url
        assert "reports" in url
