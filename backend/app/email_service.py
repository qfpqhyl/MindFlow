"""
Email service using SMTP (Feishu)
"""
import aiosmtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Email service for sending notifications"""

    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.email_from
        self.use_tls = settings.email_use_tls

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether body is HTML (default: False)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            if html:
                html_part = MIMEText(body, "html")
                message.attach(html_part)
            else:
                text_part = MIMEText(body, "plain")
                message.attach(text_part)

            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_task_reminder(
        self,
        to_email: str,
        task_title: str,
        task_description: Optional[str],
        due_date: str
    ) -> bool:
        """
        Send a task reminder email

        Args:
            to_email: Recipient email address
            task_title: Task title
            task_description: Task description (optional)
            due_date: Task due date

        Returns:
            bool: True if successful, False otherwise
        """
        subject = f"任务提醒: {task_title}"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
                .task-title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .task-description {{ margin-bottom: 15px; }}
                .due-date {{ color: #e74c3c; font-weight: bold; }}
                .footer {{ margin-top: 20px; text-align: center; color: #777; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📋 MindFlow 任务提醒</h2>
                </div>
                <div class="content">
                    <p class="task-title">{task_title}</p>
                    {f'<p class="task-description">{task_description}</p>' if task_description else ''}
                    <p>截止日期: <span class="due-date">{due_date}</span></p>
                    <p>请及时完成您的任务。</p>
                </div>
                <div class="footer">
                    <p>此邮件由 MindFlow 自动发送，请勿回复。</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
MindFlow 任务提醒

任务标题: {task_title}
{f'任务描述: {task_description}' if task_description else ''}
截止日期: {due_date}

请及时完成您的任务。

此邮件由 MindFlow 自动发送，请勿回复。
        """

        # Try HTML first, fallback to plain text
        return await self.send_email(to_email, subject, html_body, html=True)


# Global email service instance
email_service = EmailService()
