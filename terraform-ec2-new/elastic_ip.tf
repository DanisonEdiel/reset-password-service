# Elastic IP para instancias EC2 (compatible con cuentas federadas)
resource "aws_eip" "ec2_eip" {
  count = var.desired_capacity # Crear tantas EIPs como instancias deseadas
  
  domain = "vpc"
  
  tags = {
    Name        = "${var.app_name}-eip-${count.index}"
    Environment = var.environment
  }
}

# Output para mostrar la IP elástica asignada
output "elastic_ip" {
  value       = aws_eip.ec2_eip.*.public_ip
  description = "Las direcciones IP elásticas asignadas"
}

# Nota: Para asociar manualmente la IP elástica a la instancia EC2:
# 1. Obtén el ID de la instancia EC2 y el ID de asignación de la IP elástica
# 2. Usa el comando AWS CLI: aws ec2 associate-address --instance-id <ID_INSTANCIA> --allocation-id <ID_ASIGNACION>
# 3. Asegúrate de tener las credenciales AWS cargadas con: . .\set-aws-credentials.ps1
