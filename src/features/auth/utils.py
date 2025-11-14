from src.core.config import settings
from src.core.mail import send_email


async def send_token_to_user(token: str, email: str):
    await send_email(subject='Password Reset',
                     context={
                         'token': token,
                         'web_url': settings.web_url,
                     },
                     to=[email],
                     template_name='auth/password-reset.html')

async def notify_user_of_password_reset(email: str):
    await send_email(subject='Password Reset Successfully',
                     to=[email],
                     context={'web_url': settings.web_url},
                     template_name='auth/password-reset-success.html')
