from src.core.logger import logger


async def send_sms(message: str, to: str):
    logger.info("Sending text message to '{}...'", to[:7])
    print(message)
