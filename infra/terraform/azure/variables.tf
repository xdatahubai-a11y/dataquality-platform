variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "test"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "sku_name" {
  description = "PostgreSQL Flexible Server SKU"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "container_image" {
  description = "Container image URI (leave empty for placeholder)"
  type        = string
  default     = ""
}
