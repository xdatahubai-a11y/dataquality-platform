variable "cloud_provider" {
  type = string
}

variable "environment" {
  type    = string
  default = "test"
}

variable "project" {
  type    = string
  default = "dataquality-platform"
}

variable "container_image" {
  description = "Container image URI"
  type        = string
  default     = ""
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "cpu" {
  type    = number
  default = 256
}

variable "memory" {
  type    = number
  default = 512
}

variable "db_connection_string" {
  type      = string
  sensitive = true
  default   = ""
}

variable "storage_endpoint" {
  type    = string
  default = ""
}

# AWS-specific
variable "region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_id" {
  type    = string
  default = ""
}

variable "public_subnet_ids" {
  type    = list(string)
  default = []
}

variable "private_subnet_ids" {
  type    = list(string)
  default = []
}

variable "alb_security_group_id" {
  type    = string
  default = ""
}

variable "api_security_group_id" {
  type    = string
  default = ""
}

variable "s3_bucket_arn" {
  type    = string
  default = ""
}

# Azure-specific
variable "location" {
  type    = string
  default = "eastus"
}

variable "resource_group_name" {
  type    = string
  default = ""
}

variable "app_subnet_id" {
  type    = string
  default = ""
}

variable "log_analytics_workspace_id" {
  type    = string
  default = ""
}
