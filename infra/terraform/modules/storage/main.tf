locals {
  tags = {
    Environment = var.environment
    Project     = var.project
  }
  # Sanitize name for storage accounts (lowercase, no hyphens, max 24 chars)
  storage_account_name = substr(replace(lower("${var.project}${var.environment}"), "-", ""), 0, 24)
}

# ─── AWS: S3 ─────────────────────────────────────────────────────────────────

resource "aws_s3_bucket" "main" {
  count  = var.cloud_provider == "aws" ? 1 : 0
  bucket = "${var.project}-${var.environment}-data"
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "main" {
  count  = var.cloud_provider == "aws" ? 1 : 0
  bucket = aws_s3_bucket.main[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  count  = var.cloud_provider == "aws" ? 1 : 0
  bucket = aws_s3_bucket.main[0].id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "main" {
  count                   = var.cloud_provider == "aws" ? 1 : 0
  bucket                  = aws_s3_bucket.main[0].id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ─── Azure: Storage Account + ADLS Gen2 ──────────────────────────────────────

resource "azurerm_storage_account" "main" {
  count                    = var.cloud_provider == "azure" ? 1 : 0
  name                     = local.storage_account_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # Enables ADLS Gen2
  tags                     = local.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "main" {
  count              = var.cloud_provider == "azure" ? 1 : 0
  name               = "dataquality"
  storage_account_id = azurerm_storage_account.main[0].id
}
