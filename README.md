# Reset Password Service

Este microservicio es responsable de gestionar el proceso de restablecimiento de contraseñas para los usuarios registrados en el sistema. Trabaja en conjunto con el microservicio `auth-login-signup-service` para proporcionar una solución completa de autenticación.

## Características

- Solicitud de restablecimiento de contraseña vía email
- Validación de tokens de restablecimiento
- Actualización segura de contraseñas
- Registro de eventos de usuario
- Integración con Kafka para mensajería de eventos
- Documentación automática con Swagger/OpenAPI

## Arquitectura

El microservicio sigue una arquitectura por capas (N-capas) con las siguientes capas:

- **API**: Controladores y rutas FastAPI
- **Servicios**: Lógica de negocio
- **Repositorios**: Acceso a datos
- **Modelos**: Entidades de base de datos y esquemas Pydantic

## Requisitos

- Python 3.9+
- PostgreSQL
- Kafka (opcional, para mensajería de eventos)
- SMTP Server (para envío de emails)

## Configuración

Las variables de entorno se pueden configurar en un archivo `.env` en la raíz del proyecto:

```
DATABASE_URL=postgresql://user:password@localhost:5432/auth_db
JWT_SECRET=your-secret-key
MESSAGE_BROKER_URL=kafka://localhost:9092
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-password
EMAIL_FROM=noreply@example.com
```

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Configurar variables de entorno
4. Ejecutar el servidor:
   ```
   uvicorn app.main:app --reload --port 8001
   ```

## Endpoints

- `POST /password/reset-request`: Solicitar restablecimiento de contraseña
- `POST /password/reset-confirm`: Confirmar restablecimiento con token
- `GET /password/health`: Verificar estado del servicio
- `POST /password/events/user-registered`: Endpoint para recibir eventos de registro de usuarios

## Integración con auth-login-signup-service

Este microservicio está diseñado para trabajar en conjunto con `auth-login-signup-service`:

- Comparte el mismo modelo de datos de usuarios
- Utiliza los mismos tokens JWT para autenticación
- Procesa eventos generados por el servicio de autenticación
- Mantiene la misma estructura de proyecto y convenciones de código

## Pruebas

Ejecutar pruebas unitarias:

```
pytest
```

## Documentación API

La documentación Swagger está disponible en:

```
http://localhost:8001/docs
```

## Licencia

MIT
