# En lugar de crear una nueva instancia RDS, usamos la existente del servicio de autenticación
# Referencia a la base de datos RDS existente
data "aws_db_instance" "auth_db" {
  db_instance_identifier = "auth-db"
}

# Variables locales para la conexión a la base de datos
locals {
  db_host     = data.aws_db_instance.auth_db.address
  db_port     = data.aws_db_instance.auth_db.port
  db_name     = "users_db"  # Nombre de la base de datos existente
  db_username = "postgres"  # Usuario existente
  db_password = var.db_password  # Usamos la misma contraseña que está en las variables
}

# SNS Topic para notificaciones de usuario
resource "aws_sns_topic" "user_events" {
  name = "${var.app_name}-user-events"

  tags = {
    Name        = "${var.app_name}-user-events"
    Environment = var.environment
  }
}
