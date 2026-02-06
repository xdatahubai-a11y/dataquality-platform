output "api_endpoint" {
  description = "API load balancer URL"
  value       = module.compute.api_endpoint
}

output "database_host" {
  description = "RDS PostgreSQL hostname"
  value       = module.database.host
}

output "database_connection_string" {
  description = "PostgreSQL connection string"
  value       = module.database.connection_string
  sensitive   = true
}

output "s3_bucket" {
  description = "S3 bucket name"
  value       = module.storage.bucket_name
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = module.compute.ecr_repository_url
}

output "storage_endpoint" {
  description = "S3 endpoint"
  value       = module.storage.storage_endpoint
}
