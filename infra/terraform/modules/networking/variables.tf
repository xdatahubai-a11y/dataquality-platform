variable "cloud_provider" {
  description = "Cloud provider: aws or azure"
  type        = string
  validation {
    condition     = contains(["aws", "azure"], var.cloud_provider)
    error_message = "cloud_provider must be aws or azure."
  }
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "test"
}

variable "project" {
  description = "Project name for tagging"
  type        = string
  default     = "dataquality-platform"
}

# AWS-specific
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# Azure-specific
variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = ""
}

variable "vnet_address_space" {
  description = "Azure VNet address space"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}
