# Script para asociar manualmente una IP elástica a una instancia EC2
# Compatible con cuentas federadas de AWS

# Parámetros (editar estos valores)
$instanceId = ""  # Reemplazar con el ID de tu instancia EC2 para reset-password
$allocationId = ""  # Reemplazar con el ID de asignación de la IP elástica

# 1. Cargar credenciales AWS desde el script existente
Write-Host "Cargando credenciales AWS..." -ForegroundColor Cyan
. .\set-aws-credentials.ps1

# 2. Verificar que las credenciales estén cargadas
Write-Host "Verificando credenciales AWS..." -ForegroundColor Cyan
try {
    $identity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Host "Credenciales verificadas correctamente." -ForegroundColor Green
    Write-Host "Usuario: $($identity.Arn)" -ForegroundColor Green
} catch {
    Write-Host "Error al verificar credenciales AWS. Asegúrate de ejecutar set-aws-credentials.ps1 primero." -ForegroundColor Red
    exit 1
}

# 3. Asociar la IP elástica a la instancia EC2
Write-Host "Asociando IP elástica ($allocationId) a la instancia EC2 ($instanceId)..." -ForegroundColor Cyan
try {
    $result = aws ec2 associate-address --instance-id $instanceId --allocation-id $allocationId | ConvertFrom-Json
    Write-Host "IP elástica asociada correctamente." -ForegroundColor Green
    Write-Host "Association ID: $($result.AssociationId)" -ForegroundColor Green
} catch {
    Write-Host "Error al asociar la IP elástica: $_" -ForegroundColor Red
    exit 1
}

# 4. Obtener la IP pública asignada
Write-Host "Obteniendo información de la IP elástica..." -ForegroundColor Cyan
try {
    $eipInfo = aws ec2 describe-addresses --allocation-ids $allocationId | ConvertFrom-Json
    $publicIp = $eipInfo.Addresses[0].PublicIp
    Write-Host "IP pública asignada: $publicIp" -ForegroundColor Green
    
    # Mostrar información para GitHub Actions
    Write-Host "`nPara configurar GitHub Actions, usa estos valores:" -ForegroundColor Yellow
    Write-Host "EC2_HOST: $publicIp" -ForegroundColor Yellow
} catch {
    Write-Host "Error al obtener información de la IP elástica: $_" -ForegroundColor Red
}
