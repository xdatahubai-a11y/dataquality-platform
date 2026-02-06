terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
  }
}

provider "azurerm" {
  features {}
}

locals {
  project = "dataquality-platform"
  tags = {
    Environment = var.environment
    Project     = local.project
    ManagedBy   = "terraform"
  }
}

resource "azurerm_resource_group" "main" {
  name     = "${local.project}-${var.environment}-rg"
  location = var.location
  tags     = local.tags
}

module "networking" {
  source              = "../modules/networking"
  cloud_provider      = "azure"
  environment         = var.environment
  project             = local.project
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

module "monitoring" {
  source              = "../modules/monitoring"
  cloud_provider      = "azure"
  environment         = var.environment
  project             = local.project
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

module "database" {
  source              = "../modules/database"
  cloud_provider      = "azure"
  environment         = var.environment
  project             = local.project
  db_password         = var.db_password
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  sku_name            = var.sku_name
  db_subnet_id        = module.networking.db_subnet_id
}

module "storage" {
  source              = "../modules/storage"
  cloud_provider      = "azure"
  environment         = var.environment
  project             = local.project
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

module "compute" {
  source                     = "../modules/compute"
  cloud_provider             = "azure"
  environment                = var.environment
  project                    = local.project
  location                   = var.location
  resource_group_name        = azurerm_resource_group.main.name
  container_image            = var.container_image
  db_connection_string       = module.database.connection_string
  storage_endpoint           = module.storage.storage_endpoint
  app_subnet_id              = module.networking.app_subnet_id
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
}

# Key Vault for secrets
resource "azurerm_key_vault" "main" {
  name                       = substr(replace("${local.project}-${var.environment}-kv", "-", ""), 0, 24)
  location                   = var.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
  tags                       = local.tags
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault_secret" "db_password" {
  name         = "db-password"
  value        = var.db_password
  key_vault_id = azurerm_key_vault.main.id
}
