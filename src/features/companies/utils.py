from src.core.logger import logger
from src.core.mail import send_email

from src.core.config import settings


async def notify_staff_of_add(company_name: str,
                              adder_email: str,
                              email: str,
                              password: str):
    logger.info('Notifying staff of add: {}', email)

    await send_email(subject='New Account',
                     context={
                         'company': company_name,
                         'adder_email': adder_email,
                         'email': email,
                         'password': password,
                         'web_url': settings.web_url,
                     },
                     to=[email],
                     template_name='staff-add.html')
