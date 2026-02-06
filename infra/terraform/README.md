# DataQuality Platform — Terraform Infrastructure

Modular Terraform setup supporting both AWS and Azure deployments.

## Architecture

```
modules/          Shared modules (cloud_provider switch)
  networking/     VPC (AWS) or VNet (Azure)
  database/       RDS PostgreSQL (AWS) or Flexible Server (Azure)
  storage/        S3 (AWS) or ADLS Gen2 (Azure)
  compute/        ECS Fargate + ALB (AWS) or Container Apps (Azure)
  monitoring/     CloudWatch (AWS) or Log Analytics (Azure)
aws/              AWS root configuration
azure/            Azure root configuration
```

## Deploy to AWS

```bash
cd infra/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

## Deploy to Azure

```bash
cd infra/terraform/azure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

## Remote State

Each cloud directory includes a `backend.tf` with commented-out remote state configuration. Uncomment and configure before production use.

## Destroying

```bash
terraform destroy
```
