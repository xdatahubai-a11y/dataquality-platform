locals {
  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

# ─── AWS: RDS PostgreSQL ─────────────────────────────────────────────────────

resource "aws_db_subnet_group" "main" {
  count      = var.cloud_provider == "aws" ? 1 : 0
  name       = "${var.project}-${var.environment}-db-subnet"
  subnet_ids = var.private_subnet_ids
  tags       = local.tags
}

resource "aws_db_instance" "main" {
  count                  = var.cloud_provider == "aws" ? 1 : 0
  identifier             = "${var.project}-${var.environment}-pg"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = var.instance_class
  allocated_storage      = 20
  max_allocated_storage  = 50
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  vpc_security_group_ids = [var.db_security_group_id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  storage_encrypted      = true
  tags                   = local.tags
}

# ─── Azure: PostgreSQL Flexible Server ────────────────────────────────────────

resource "azurerm_private_dns_zone" "postgres" {
  count               = var.cloud_provider == "azure" ? 1 : 0
  name                = "${var.project}-${var.environment}.postgres.database.azure.com"
  resource_group_name = var.resource_group_name
  tags                = local.tags
}

resource "azurerm_postgresql_flexible_server" "main" {
  count                  = var.cloud_provider == "azure" ? 1 : 0
  name                   = "${var.project}-${var.environment}-pg"
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "15"
  administrator_login    = var.db_username
  administrator_password = var.db_password
  sku_name               = var.sku_name
  storage_mb             = 32768
  zone                   = "1"
  delegated_subnet_id    = var.db_subnet_id
  private_dns_zone_id    = azurerm_private_dns_zone.postgres[0].id
  tags                   = local.tags
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  count     = var.cloud_provider == "azure" ? 1 : 0
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.main[0].id
  charset   = "UTF8"
  collation = "en_US.utf8"
}
