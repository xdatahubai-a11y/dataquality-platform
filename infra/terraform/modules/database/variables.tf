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

variable "db_name" {
  type    = string
  default = "dataquality"
}

variable "db_username" {
  type    = string
  default = "dq"
}

variable "db_password" {
  type      = string
  sensitive = true
}

# AWS-specific
variable "instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "vpc_id" {
  type    = string
  default = ""
}

variable "private_subnet_ids" {
  type    = list(string)
  default = []
}

variable "db_security_group_id" {
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

variable "sku_name" {
  type    = string
  default = "B_Standard_B1ms"
}

variable "db_subnet_id" {
  type    = string
  default = ""
}
