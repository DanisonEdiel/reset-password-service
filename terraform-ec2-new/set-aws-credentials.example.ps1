# Script para configurar credenciales de AWS como variables de entorno
# Renombrar a set-aws-credentials.ps1 y completar con tus credenciales

# AWS Credentials
$env:AWS_ACCESS_KEY_ID = "tu-access-key"
$env:AWS_SECRET_ACCESS_KEY = "tu-secret-key"
$env:AWS_SESSION_TOKEN = "tu-session-token-si-aplica"

# Región
$env:AWS_REGION = "us-east-1"

Write-Host "Credenciales de AWS configuradas correctamente"
