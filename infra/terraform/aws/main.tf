terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "dataquality-platform"
      ManagedBy   = "terraform"
    }
  }
}

locals {
  project = "dataquality-platform"
  azs     = ["${var.region}a", "${var.region}b"]
}

module "networking" {
  source             = "../modules/networking"
  cloud_provider     = "aws"
  environment        = var.environment
  project            = local.project
  region             = var.region
  availability_zones = local.azs
}

module "database" {
  source               = "../modules/database"
  cloud_provider       = "aws"
  environment          = var.environment
  project              = local.project
  db_password          = var.db_password
  instance_class       = var.instance_class
  vpc_id               = module.networking.vpc_id
  private_subnet_ids   = module.networking.private_subnet_ids
  db_security_group_id = module.networking.db_security_group_id
}

module "storage" {
  source         = "../modules/storage"
  cloud_provider = "aws"
  environment    = var.environment
  project        = local.project
}

module "monitoring" {
  source         = "../modules/monitoring"
  cloud_provider = "aws"
  environment    = var.environment
  project        = local.project
}

module "compute" {
  source                = "../modules/compute"
  cloud_provider        = "aws"
  environment           = var.environment
  project               = local.project
  region                = var.region
  container_image       = var.container_image
  db_connection_string  = module.database.connection_string
  storage_endpoint      = module.storage.storage_endpoint
  vpc_id                = module.networking.vpc_id
  public_subnet_ids     = module.networking.public_subnet_ids
  private_subnet_ids    = module.networking.private_subnet_ids
  alb_security_group_id = module.networking.alb_security_group_id
  api_security_group_id = module.networking.api_security_group_id
  s3_bucket_arn         = "arn:aws:s3:::${module.storage.bucket_name}"
}

# Secrets Manager for DB credentials
resource "aws_secretsmanager_secret" "db_password" {
  name = "${local.project}-${var.environment}-db-password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}
