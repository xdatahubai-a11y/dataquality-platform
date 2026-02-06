locals {
  tags = {
    Environment = var.environment
    Project     = var.project
  }
}

# ─── AWS: ECS Fargate + ALB + ECR ────────────────────────────────────────────

resource "aws_ecr_repository" "main" {
  count                = var.cloud_provider == "aws" ? 1 : 0
  name                 = "${var.project}-${var.environment}"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
  tags = local.tags
}

resource "aws_ecs_cluster" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  name  = "${var.project}-${var.environment}"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = local.tags
}

resource "aws_iam_role" "ecs_task_execution" {
  count = var.cloud_provider == "aws" ? 1 : 0
  name  = "${var.project}-${var.environment}-ecs-exec"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "ecs_exec" {
  count      = var.cloud_provider == "aws" ? 1 : 0
  role       = aws_iam_role.ecs_task_execution[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  count = var.cloud_provider == "aws" ? 1 : 0
  name  = "${var.project}-${var.environment}-ecs-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
  tags = local.tags
}

resource "aws_iam_role_policy" "ecs_task_s3" {
  count = var.cloud_provider == "aws" ? 1 : 0
  name  = "s3-access"
  role  = aws_iam_role.ecs_task[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource = [var.s3_bucket_arn, "${var.s3_bucket_arn}/*"]
    }]
  })
}

resource "aws_lb" "main" {
  count              = var.cloud_provider == "aws" ? 1 : 0
  name               = "${var.project}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids
  tags               = local.tags
}

resource "aws_lb_target_group" "main" {
  count       = var.cloud_provider == "aws" ? 1 : 0
  name        = "${var.project}-${var.environment}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
  }
  tags = local.tags
}

resource "aws_lb_listener" "main" {
  count             = var.cloud_provider == "aws" ? 1 : 0
  load_balancer_arn = aws_lb.main[0].arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main[0].arn
  }
}

resource "aws_cloudwatch_log_group" "main" {
  count             = var.cloud_provider == "aws" ? 1 : 0
  name              = "/ecs/${var.project}-${var.environment}"
  retention_in_days = 30
  tags              = local.tags
}

resource "aws_ecs_task_definition" "main" {
  count                    = var.cloud_provider == "aws" ? 1 : 0
  family                   = "${var.project}-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = tostring(var.cpu)
  memory                   = tostring(var.memory)
  execution_role_arn       = aws_iam_role.ecs_task_execution[0].arn
  task_role_arn            = aws_iam_role.ecs_task[0].arn

  container_definitions = jsonencode([{
    name      = "api"
    image     = var.container_image != "" ? var.container_image : "${aws_ecr_repository.main[0].repository_url}:latest"
    essential = true
    portMappings = [{ containerPort = var.container_port, protocol = "tcp" }]
    environment = [
      { name = "DQ_DATABASE_URL", value = var.db_connection_string },
      { name = "DQ_STORAGE_ENDPOINT", value = var.storage_endpoint },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.main[0].name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
  tags = local.tags
}

resource "aws_ecs_service" "main" {
  count           = var.cloud_provider == "aws" ? 1 : 0
  name            = "${var.project}-${var.environment}-api"
  cluster         = aws_ecs_cluster.main[0].id
  task_definition = aws_ecs_task_definition.main[0].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.private_subnet_ids
    security_groups = [var.api_security_group_id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main[0].arn
    container_name   = "api"
    container_port   = var.container_port
  }

  tags = local.tags
}

# ─── Azure: Container Apps + ACR ─────────────────────────────────────────────

resource "azurerm_container_registry" "main" {
  count               = var.cloud_provider == "azure" ? 1 : 0
  name                = replace("${var.project}${var.environment}acr", "-", "")
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = local.tags
}

resource "azurerm_container_app_environment" "main" {
  count                      = var.cloud_provider == "azure" ? 1 : 0
  name                       = "${var.project}-${var.environment}-env"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  infrastructure_subnet_id   = var.app_subnet_id
  log_analytics_workspace_id = var.log_analytics_workspace_id
  tags                       = local.tags
}

resource "azurerm_container_app" "main" {
  count                        = var.cloud_provider == "azure" ? 1 : 0
  name                         = "${var.project}-${var.environment}-api"
  container_app_environment_id = azurerm_container_app_environment.main[0].id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  tags                         = local.tags

  template {
    container {
      name   = "api"
      image  = var.container_image != "" ? var.container_image : "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = var.cpu / 1000.0
      memory = "${var.memory / 1024.0}Gi"

      env {
        name  = "DQ_DATABASE_URL"
        value = var.db_connection_string
      }
      env {
        name  = "DQ_STORAGE_ENDPOINT"
        value = var.storage_endpoint
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = var.container_port
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}
