import time
from typing import TYPE_CHECKING
import logging

from config import (
    get_connection,
    configure_logging,
    MQ_ROUTING_KEY,
)

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

log = logging.getLogger(__name__)


def process_new_message(
    ch: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    log.debug("ch: %s", ch)
    log.debug("method: %s", method)
    log.debug("properties: %s", properties)
    log.debug("body: %s", body)

    log.warning("[ ] Start processing message (expensive task!) %r", body)
    start_time = time.time()

    number = int(body[-2:])
    is_odd = number % 2
    ...
    time.sleep(1 + is_odd * 2)
    ...
    end_time = time.time()
    log.info("Finished processing message %r, sending ack!", body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    log.warning(
        "[X] Finished in %.2fs processing message %r",
        end_time - start_time,
        body,
    )


def consume_messages(channel: "BlockingChannel") -> None:
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=MQ_ROUTING_KEY,
        on_message_callback=process_new_message,
        # auto_ack=True,
    )
    log.warning("Waiting for messages...")
    channel.start_consuming()


def main():
    configure_logging(level=logging.WARNING)
    with get_connection() as connection:
        log.info("Created connection: %s", connection)
        with connection.channel() as channel:
            log.info("Created channel: %s", channel)
            consume_messages(channel=channel)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
