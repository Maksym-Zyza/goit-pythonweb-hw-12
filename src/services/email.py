from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors

from pathlib import Path
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME="84aee78bd90d0a",
    MAIL_PASSWORD="156f2b90dbd43e",
    MAIL_FROM="mmziza88@gmail.com",
    MAIL_PORT=2525,
    MAIL_SERVER="sandbox.smtp.mailtrap.io",
    MAIL_FROM_NAME="Contacts App",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)

"""
Модуль сервісу відправки email повідомлень.

Використовує FastAPI-Mail для відправки підтвердження email та скидання пароля.
"""


async def send_email(email: str, username: str, host: str):
    """
    Відправляє email для підтвердження реєстрації користувача.

    Генерує JWT токен підтвердження email та відправляє лист з посиланням.

    Args:
        email (str): Email отримувача.
        username (str): Ім'я користувача.
        host (str): Базовий URL сервера (для формування посилання).

    Raises:
        ConnectionErrors: У разі проблем з відправкою листа.
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(email: str, username: str, reset_link: str):
    """
    Відправляє email з посиланням на форму скидання пароля.

    Args:
        email (str): Email отримувача.
        username (str): Ім'я користувача.
        reset_link (str): Посилання для скидання пароля.

    Raises:
        ConnectionErrors: У разі проблем з відправкою листа.
    """
    try:
        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            template_body={
                "username": username,
                "reset_link": reset_link,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password_template.html")
    except ConnectionErrors as err:
        print(err)
