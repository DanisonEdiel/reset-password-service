variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key_id" {
  description = "AWS access key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS secret key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "aws_session_token" {
  description = "AWS session token"
  type        = string
  default     = ""
  sensitive   = true
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "reset-password-service"
}

variable "environment" {
  description = "Environment (dev, prod, etc.)"
  type        = string
  default     = "dev"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "ecr_repository_url" {
  description = "ECR repository URL"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key for EC2 instances"
  type        = string
}

variable "desired_capacity" {
  description = "Número deseado de instancias EC2 en el Auto Scaling Group"
  type        = number
  default     = 1
}

variable "smtp_username" {
  description = "SMTP username for sending emails"
  type        = string
  default     = ""
  sensitive   = true
}

variable "smtp_password" {
  description = "SMTP password for sending emails"
  type        = string
  default     = ""
  sensitive   = true
}

variable "email_from" {
  description = "Email address to send emails from"
  type        = string
  default     = "noreply@example.com"
}

variable "create_resources" {
  description = "Mapa de recursos a crear (true) o no crear (false)"
  type        = map(bool)
  default     = {
    security_groups = true
    key_pair        = true
    db_subnet_group = true
    ecs_cluster     = true
    log_group       = true
    iam_role        = true
    target_group    = true
  }
}
