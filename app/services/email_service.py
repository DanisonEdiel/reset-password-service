import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger

from app.core.config import settings


class EmailService:
    """
    Service for sending emails
    """

    async def send_login_notification(self, user_email: str, login_time: str, ip_address: str = None) -> bool:
        """
        Send login notification email
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_SENDER
            msg['To'] = user_email
            msg['Subject'] = f"Inicio de sesión detectado - {settings.PROJECT_NAME}"

            # Create HTML body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
                    <h2 style="color: #333;">Notificación de inicio de sesión</h2>
                    <p>Hemos detectado un inicio de sesión en tu cuenta.</p>
                    <p><strong>Fecha y hora:</strong> {login_time}</p>
                    {"<p><strong>Dirección IP:</strong> " + ip_address + "</p>" if ip_address else ""}
                    <p>Si no reconoces esta actividad, por favor cambia tu contraseña inmediatamente.</p>
                    <p>Gracias,<br>El equipo de {settings.PROJECT_NAME}</p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Connect to SMTP server and send email
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()

                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

                server.send_message(msg)

            logger.info(f"Login notification email sent to {user_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send login notification email: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()