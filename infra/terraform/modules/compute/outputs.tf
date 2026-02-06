output "api_endpoint" {
  description = "API endpoint URL"
  value = var.cloud_provider == "aws" ? (
    length(aws_lb.main) > 0 ? "http://${aws_lb.main[0].dns_name}" : ""
  ) : (
    length(azurerm_container_app.main) > 0 ? "https://${azurerm_container_app.main[0].latest_revision_fqdn}" : ""
  )
}

output "ecr_repository_url" {
  description = "ECR repository URL (AWS only)"
  value       = var.cloud_provider == "aws" && length(aws_ecr_repository.main) > 0 ? aws_ecr_repository.main[0].repository_url : ""
}

output "acr_login_server" {
  description = "ACR login server (Azure only)"
  value       = var.cloud_provider == "azure" && length(azurerm_container_registry.main) > 0 ? azurerm_container_registry.main[0].login_server : ""
}
