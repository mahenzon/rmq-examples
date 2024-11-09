import logging

import pika

RMQ_HOST = "0.0.0.0"
RMQ_PORT = 5672

RMQ_USER = "guest"
RMQ_PASSWORD = "guest"

MQ_EXCHANGE = ""
MQ_ROUTING_KEY = "news"

MQ_NEWS_SIMPLE_DEAD_LETTER_EXCHANGE = "dlx-news"
MQ_NEWS_SIMPLE_DEAD_LETTER_KEY = "dlq-news"

MQ_EMAIL_UPDATES_EXCHANGE_NAME = "email-updates"
MQ_QUEUE_NAME_KYC_EMAIL_UPDATES = "kyc-email-updates"
MQ_QUEUE_NAME_NEWSLETTER_EMAIL_UPDATES = "newsletter-email-updates"

MQ_QUEUE_NAME_WEATHER_UPDATES = "q-weather-updates"
MQ_QUEUE_WEATHER_UPDATES_TTL = 60_000  # TTL of 60 seconds
MQ_DLQ_NAME_EXPIRED_WEATHER_UPDATES = "q-expired-weather-updates"
MQ_DLQ_EXPIRED_WEATHER_UPDATES_TTL = 120_000  # TTL of 2 minutes


# DEFAULT_LOG_FORMAT = "[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
# DEFAULT_LOG_FORMAT = "%(name)s %(module)s:%(lineno)d %(levelname)-6s - %(message)s"
DEFAULT_LOG_FORMAT = "%(module)s:%(lineno)d %(levelname)-6s - %(message)s"


connection_params = pika.ConnectionParameters(
    host=RMQ_HOST,
    port=RMQ_PORT,
    credentials=pika.PlainCredentials(RMQ_USER, RMQ_PASSWORD),
)


def get_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(
        parameters=connection_params,
    )


def configure_logging(
    level: int = logging.INFO,
    pika_log_level: int = logging.WARNING,
) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=DEFAULT_LOG_FORMAT,
        # format="%(message)s",
    )
    logging.getLogger("pika").setLevel(pika_log_level)
