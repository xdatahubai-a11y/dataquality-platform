output "api_endpoint" {
  description = "Container App URL"
  value       = module.compute.api_endpoint
}

output "database_host" {
  description = "PostgreSQL Flexible Server hostname"
  value       = module.database.host
}

output "database_connection_string" {
  description = "PostgreSQL connection string"
  value       = module.database.connection_string
  sensitive   = true
}

output "storage_endpoint" {
  description = "ADLS Gen2 endpoint"
  value       = module.storage.storage_endpoint
}

output "storage_account_name" {
  description = "Azure Storage account name"
  value       = module.storage.storage_account_name
}

output "acr_login_server" {
  description = "ACR login server"
  value       = module.compute.acr_login_server
}
