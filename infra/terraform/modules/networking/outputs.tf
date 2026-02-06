output "vpc_id" {
  description = "AWS VPC ID"
  value       = var.cloud_provider == "aws" ? aws_vpc.main[0].id : null
}

output "vnet_id" {
  description = "Azure VNet ID"
  value       = var.cloud_provider == "azure" ? azurerm_virtual_network.main[0].id : null
}

output "public_subnet_ids" {
  description = "AWS public subnet IDs"
  value       = var.cloud_provider == "aws" ? aws_subnet.public[*].id : []
}

output "private_subnet_ids" {
  description = "AWS private subnet IDs"
  value       = var.cloud_provider == "aws" ? aws_subnet.private[*].id : []
}

output "app_subnet_id" {
  description = "Azure app subnet ID"
  value       = var.cloud_provider == "azure" ? azurerm_subnet.app[0].id : null
}

output "db_subnet_id" {
  description = "Azure DB subnet ID"
  value       = var.cloud_provider == "azure" ? azurerm_subnet.db[0].id : null
}

output "alb_security_group_id" {
  description = "AWS ALB security group ID"
  value       = var.cloud_provider == "aws" ? aws_security_group.alb[0].id : null
}

output "api_security_group_id" {
  description = "AWS API security group ID"
  value       = var.cloud_provider == "aws" ? aws_security_group.api[0].id : null
}

output "db_security_group_id" {
  description = "AWS DB security group ID"
  value       = var.cloud_provider == "aws" ? aws_security_group.db[0].id : null
}

output "nsg_id" {
  description = "Azure NSG ID"
  value       = var.cloud_provider == "azure" ? azurerm_network_security_group.main[0].id : null
}
