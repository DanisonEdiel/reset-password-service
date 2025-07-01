import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from loguru import logger

from app.core.config import settings


class EmailService:
    """
    Service for sending emails
    """
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        cc: List[str] = None,
        bcc: List[str] = None
    ) -> bool:
        """
        Send email using SMTP
        """
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Email not sent.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = settings.EMAIL_FROM
            message["To"] = to_email
            message["Subject"] = subject
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)
            
            # Attach HTML content
            message.attach(MIMEText(html_content, "html"))
            
            # Connect to SMTP server
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                # Send email
                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)
                
                server.sendmail(settings.EMAIL_FROM, recipients, message.as_string())
            
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset email
        """
        subject = "Reset Your Password"
        reset_url = f"https://yourdomain.com/reset-password?token={reset_token}"
        
        html_content = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Please click the link below to reset your password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>If you did not request a password reset, please ignore this email.</p>
                <p>This link will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
                <p>Best regards,<br>Your Application Team</p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
