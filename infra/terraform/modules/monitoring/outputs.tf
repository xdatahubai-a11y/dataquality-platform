output "log_group_name" {
  description = "AWS CloudWatch log group name"
  value       = var.cloud_provider == "aws" && length(aws_cloudwatch_log_group.app) > 0 ? aws_cloudwatch_log_group.app[0].name : ""
}

output "log_analytics_workspace_id" {
  description = "Azure Log Analytics workspace ID"
  value       = var.cloud_provider == "azure" && length(azurerm_log_analytics_workspace.main) > 0 ? azurerm_log_analytics_workspace.main[0].id : ""
}
