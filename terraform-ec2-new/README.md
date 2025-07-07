# Terraform AWS ECS EC2 Deployment - Reset Password Service

Este directorio contiene la configuración de Terraform para desplegar el servicio de restablecimiento de contraseña en AWS ECS con instancias EC2, conectándose a la misma base de datos RDS que usa el servicio de autenticación.

## Configuración de credenciales AWS

Para configurar las credenciales de AWS de forma segura, sigue estos pasos:

1. Copia el archivo de ejemplo a un archivo local:
   ```
   cp set-aws-credentials.example.ps1 set-aws-credentials.ps1
   ```

2. Edita el archivo `set-aws-credentials.ps1` y añade tus credenciales AWS:
   ```powershell
   $AWS_ACCESS_KEY_ID = "TU_ACCESS_KEY_ID"
   $AWS_SECRET_ACCESS_KEY = "TU_SECRET_ACCESS_KEY"
   $AWS_SESSION_TOKEN = "TU_SESSION_TOKEN"  # Solo si usas credenciales temporales
   ```

3. Ejecuta el script para configurar las variables de entorno:
   ```powershell
   .\set-aws-credentials.ps1
   ```

> **IMPORTANTE**: El archivo `set-aws-credentials.ps1` está incluido en `.gitignore` para evitar subir credenciales al repositorio. NUNCA subas este archivo con credenciales reales al repositorio.

## Despliegue de la infraestructura

Una vez configuradas las credenciales, puedes desplegar la infraestructura:

```powershell
terraform init
terraform plan
terraform apply
```

## Componentes de la infraestructura

- **ECS Cluster**: Cluster de ECS para ejecutar el servicio de reset-password
- **EC2 Instances**: Instancias EC2 con Ubuntu 20.04 y el agente ECS
- **Conexión a RDS existente**: El servicio se conecta a la base de datos RDS existente del servicio de autenticación
- **Application Load Balancer**: Balanceador de carga para distribuir el tráfico
- **Elastic IPs**: IPs elásticas para las instancias EC2 (configuración opcional)

## Conexión a la base de datos RDS existente

Este servicio está configurado para conectarse a la misma base de datos RDS PostgreSQL que usa el servicio de autenticación (`auth-db`). No se crea una nueva base de datos, sino que se reutiliza la existente.

## Elastic IPs para instancias EC2

La configuración incluye la creación de IPs elásticas para las instancias EC2. Para asociar manualmente una IP elástica a una instancia EC2 después del despliegue:

1. Obtén los IDs de la instancia EC2 y de la IP elástica desde la consola de AWS o usando el comando:
   ```
   terraform output
   ```

2. Edita el archivo `associate_eip.ps1` con los IDs correctos.

3. Ejecuta el script:
   ```powershell
   .\associate_eip.ps1
   ```

## Notas importantes

1. Asegúrate de que el grupo de seguridad de la base de datos RDS permita conexiones desde la instancia EC2 de este servicio.
2. La contraseña de la base de datos debe ser la misma que la configurada en el servicio de autenticación.
3. Ambos servicios (autenticación y reset-password) deben estar configurados para usar la misma base de datos `users_db`.
4. Después de desplegar, actualiza las variables de entorno en GitHub Actions para incluir la nueva IP elástica.
