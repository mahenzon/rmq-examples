import time
import logging

from config import (
    configure_logging,
)
from rabbit.common import PaintButtonsRabbit


log = logging.getLogger(__name__)


class Publisher(PaintButtonsRabbit):

    def produce_message(self, idx: int) -> None:
        message_body = f"Paint buttons task #{idx:02d}"
        self.publish_message(message_body)


def main():
    configure_logging(level=logging.WARNING)
    with Publisher() as publisher:
        publisher.declare_queue()
        for idx in range(1, 33):
            publisher.produce_message(idx=idx)
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
