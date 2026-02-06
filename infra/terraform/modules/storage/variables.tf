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

# Azure-specific
variable "location" {
  type    = string
  default = "eastus"
}

variable "resource_group_name" {
  type    = string
  default = ""
}
