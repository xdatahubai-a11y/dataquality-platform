output "storage_endpoint" {
  description = "Storage endpoint URL"
  value = var.cloud_provider == "aws" ? (
    length(aws_s3_bucket.main) > 0 ? "s3://${aws_s3_bucket.main[0].bucket}" : ""
  ) : (
    length(azurerm_storage_account.main) > 0 ? azurerm_storage_account.main[0].primary_dfs_endpoint : ""
  )
}

output "bucket_name" {
  description = "S3 bucket name (AWS only)"
  value       = var.cloud_provider == "aws" && length(aws_s3_bucket.main) > 0 ? aws_s3_bucket.main[0].bucket : ""
}

output "container_name" {
  description = "ADLS container name (Azure only)"
  value       = var.cloud_provider == "azure" && length(azurerm_storage_data_lake_gen2_filesystem.main) > 0 ? azurerm_storage_data_lake_gen2_filesystem.main[0].name : ""
}

output "storage_account_name" {
  description = "Azure storage account name"
  value       = var.cloud_provider == "azure" && length(azurerm_storage_account.main) > 0 ? azurerm_storage_account.main[0].name : ""
}
