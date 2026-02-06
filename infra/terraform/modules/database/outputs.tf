output "host" {
  description = "Database hostname"
  value = var.cloud_provider == "aws" ? (
    length(aws_db_instance.main) > 0 ? aws_db_instance.main[0].address : ""
  ) : (
    length(azurerm_postgresql_flexible_server.main) > 0 ? azurerm_postgresql_flexible_server.main[0].fqdn : ""
  )
}

output "port" {
  description = "Database port"
  value       = 5432
}

output "username" {
  description = "Database username"
  value       = var.db_username
}

output "connection_string" {
  description = "PostgreSQL connection string"
  sensitive   = true
  value = var.cloud_provider == "aws" ? (
    length(aws_db_instance.main) > 0 ? "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main[0].address}:5432/${var.db_name}" : ""
  ) : (
    length(azurerm_postgresql_flexible_server.main) > 0 ? "postgresql://${var.db_username}:${var.db_password}@${azurerm_postgresql_flexible_server.main[0].fqdn}:5432/${var.db_name}" : ""
  )
}
