provider "aws" {
  region = var.aws_region
  
  # Si se proporcionan credenciales explícitas, las usamos
  access_key = var.aws_access_key_id != "" ? var.aws_access_key_id : null
  secret_key = var.aws_secret_access_key != "" ? var.aws_secret_access_key : null
  token      = var.aws_session_token != "" ? var.aws_session_token : null
  
  # De lo contrario, AWS Provider buscará credenciales en el orden estándar:
  # 1. Variables de entorno
  # 2. Archivo de credenciales compartidas (~/.aws/credentials)
  # 3. Perfil de instancia EC2
}

# VPC y Subnets
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Grupos de Seguridad
resource "aws_security_group" "alb" {
  name        = "${var.app_name}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.app_name}-alb-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "ecs" {
  name        = "${var.app_name}-ecs-sg"
  description = "Security group for ECS instances"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 8001
    to_port         = 8001
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.app_name}-ecs-sg"
    Environment = var.environment
  }
}

# En lugar de crear un nuevo grupo de seguridad para PostgreSQL, usamos el existente
# Obtenemos el grupo de seguridad de la base de datos RDS existente
data "aws_security_group" "auth_db_sg" {
  filter {
    name   = "group-name"
    values = ["auth-postgres-sg"]
  }
}

# Creamos una regla de ingreso en el grupo de seguridad existente para permitir conexiones desde nuestro servicio
resource "aws_security_group_rule" "reset_password_to_rds" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = data.aws_security_group.auth_db_sg.id
  source_security_group_id = aws_security_group.ecs.id
  description              = "Allow PostgreSQL access from reset-password service"
}

# Load Balancer
resource "aws_lb" "this" {
  name               = "${var.app_name}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids

  enable_deletion_protection = false

  tags = {
    Name        = "${var.app_name}-lb"
    Environment = var.environment
  }
}

# Target Group
resource "aws_lb_target_group" "this" {
  name     = "${var.app_name}-tg"
  port     = 8001
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id
  target_type = "instance"

  health_check {
    enabled             = true
    interval            = 30
    path                = "/password/health"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    protocol            = "HTTP"
    matcher             = "200"
  }

  tags = {
    Name        = "${var.app_name}-tg"
    Environment = var.environment
  }
}

# Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}
