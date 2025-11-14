from pathlib import Path

from fastapi import UploadFile
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.core.config import settings
from src.core.logger import logger

config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_SERVER=settings.mail_server,
    MAIL_PORT=settings.mail_port,
    MAIL_STARTTLS=settings.mail_start_tls,
    MAIL_SSL_TLS=settings.mail_use_tls,
    MAIL_FROM=settings.mail_from,
    MAIL_FROM_NAME=settings.mail_from_name,
    USE_CREDENTIALS=settings.mail_use_credentials,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(
    subject: str,
    to: list[str],
    body: str | list | None = None,
    cc: list[str] = [],
    bcc: list[str] = [],
    attachments: list[UploadFile] = [],
    context: dict | None = None,
    template_name: str | None = None,
):
    logger.info("Sending Email '{}' to {}", subject, [f'{email[:3]}...' for email in to])
    conn = FastMail(config)
    message = MessageSchema(
        subject=subject,
        body=body,
        recipients=to,
        cc=cc,
        bcc=bcc,
        subtype=MessageType.html,
        template_body=context,
        attachments=attachments,
    )

    await conn.send_message(message, template_name=template_name)
    logger.info("Email sent")
