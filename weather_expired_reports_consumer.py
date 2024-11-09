import time
from typing import TYPE_CHECKING
import logging

from config import (
    configure_logging,
    MQ_DLQ_NAME_EXPIRED_WEATHER_UPDATES,
)

from rabbit.common import WeatherRabbit

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

log = logging.getLogger(__name__)


def process_new_weather_report(
    ch: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    log.debug("ch: %s", ch)
    log.debug("method: %s", method)
    log.debug("properties: %s", properties)
    log.debug("body: %s", body)

    log.warning("[ ] Starting processing weather report %r", body)
    time.sleep(2)
    log.warning("[x] Finished processing weather report %r, sending ack!", body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    configure_logging(level=logging.INFO)
    with WeatherRabbit() as rabbit:
        rabbit.consume_messages(
            message_callback=process_new_weather_report,
            queue_name=MQ_DLQ_NAME_EXPIRED_WEATHER_UPDATES,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
