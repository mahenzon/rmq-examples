import time
import logging

import config
from rabbit.common import EmailUpdatesRabbit

from config import (
    configure_logging,
)

log = logging.getLogger(__name__)


class Producer(EmailUpdatesRabbit):

    def produce_message(self, idx: int) -> None:
        message_body = f"New message #{idx:02d}"
        log.info("Publish message %s", message_body)
        self.channel.basic_publish(
            exchange=config.MQ_EMAIL_UPDATES_EXCHANGE_NAME,
            routing_key="",
            body=message_body,
        )
        log.warning("Published message %s", message_body)


def main():
    configure_logging(level=logging.WARNING)
    with Producer() as producer:
        producer.declare_email_updates_exchange()
        for idx in range(1, 6):
            producer.produce_message(idx=idx)
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
