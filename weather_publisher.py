import time
import logging

from config import (
    configure_logging,
)
from rabbit.common import WeatherRabbit


log = logging.getLogger(__name__)


class Publisher(WeatherRabbit):

    def produce_message(self, idx: int) -> None:
        message_body = f"Weather report #{idx:04d} at {time.strftime('%H:%M:%S')}"
        self.publish_message(message_body)


def main():
    configure_logging(level=logging.INFO)
    with Publisher() as publisher:
        publisher.declare_queue()
        for idx in range(1, 3001):
            publisher.produce_message(idx=idx)
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
