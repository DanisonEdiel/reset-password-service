# ECS Cluster
resource "aws_ecs_cluster" "this" {
  name = "${var.app_name}-cluster"

  tags = {
    Name        = "${var.app_name}-cluster"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = 30

  tags = {
    Name        = "${var.app_name}-logs"
    Environment = var.environment
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "this" {
  family                   = var.app_name
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = "${var.ecr_repository_url}:${var.image_tag}"
      essential = true
      cpu       = 256
      memory    = 512
      portMappings = [
        {
          containerPort = 8001
          hostPort      = 8001
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "JWT_SECRET"
          value = var.jwt_secret
        },
        {
          name  = "POSTGRES_USER"
          value = local.db_username
        },
        {
          name  = "POSTGRES_PASSWORD"
          value = local.db_password
        },
        {
          name  = "POSTGRES_HOST"
          value = local.db_host
        },
        {
          name  = "POSTGRES_PORT"
          value = tostring(local.db_port)
        },
        {
          name  = "POSTGRES_DB"
          value = local.db_name
        },
        {
          name  = "SMTP_USERNAME"
          value = var.smtp_username
        },
        {
          name  = "SMTP_PASSWORD"
          value = var.smtp_password
        },
        {
          name  = "EMAIL_FROM"
          value = var.email_from
        }
      ]
      logConfiguration = {
        logDriver = "json-file"
        options = {
          "max-size" = "10m"
          "max-file" = "3"
        }
      }
      mountPoints = []
      volumesFrom = []
    }
  ])

  tags = {
    Name        = var.app_name
    Environment = var.environment
  }
}

# ECS Service
resource "aws_ecs_service" "this" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 1
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = var.app_name
    container_port   = 8001
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # Dependencia del listener HTTP
  depends_on = [aws_lb_listener.http]

  # No configuramos network_configuration ya que estamos usando el modo bridge en EC2
  # y no necesitamos asignar IPs públicas o subredes específicas

  # Configuración de despliegue
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  tags = {
    Name        = var.app_name
    Environment = var.environment
  }
}

# Auto Scaling
resource "aws_appautoscaling_target" "this" {
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.this.name}/${aws_ecs_service.this.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.app_name}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.this.resource_id
  scalable_dimension = aws_appautoscaling_target.this.scalable_dimension
  service_namespace  = aws_appautoscaling_target.this.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

resource "aws_appautoscaling_policy" "memory" {
  name               = "${var.app_name}-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.this.resource_id
  scalable_dimension = aws_appautoscaling_target.this.scalable_dimension
  service_namespace  = aws_appautoscaling_target.this.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 70.0
  }
}
