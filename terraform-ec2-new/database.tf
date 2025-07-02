# DB Subnet Group
resource "aws_db_subnet_group" "postgres" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name        = "${var.app_name}-db-subnet-group"
    Environment = var.environment
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier             = "${var.app_name}-db"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  username               = "postgres"
  password               = var.db_password
  db_name                = "auth_db"  # Usamos la misma base de datos que auth-login-signup-service
  parameter_group_name   = "default.postgres16"
  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.postgres.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  multi_az               = false

  tags = {
    Name        = "${var.app_name}-db"
    Environment = var.environment
  }
}

# SNS Topic para notificaciones de usuario
resource "aws_sns_topic" "user_events" {
  name = "${var.app_name}-user-events"

  tags = {
    Name        = "${var.app_name}-user-events"
    Environment = var.environment
  }
}
