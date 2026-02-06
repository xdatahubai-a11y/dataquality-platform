locals {
  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

# ─── AWS: CloudWatch ─────────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "app" {
  count             = var.cloud_provider == "aws" ? 1 : 0
  name              = "/app/${var.project}-${var.environment}"
  retention_in_days = 30
  tags              = local.tags
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count               = var.cloud_provider == "aws" ? 1 : 0
  alarm_name          = "${var.project}-${var.environment}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization high"
  tags                = local.tags
}

# ─── Azure: Log Analytics ────────────────────────────────────────────────────

resource "azurerm_log_analytics_workspace" "main" {
  count               = var.cloud_provider == "azure" ? 1 : 0
  name                = "${var.project}-${var.environment}-logs"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.tags
}
