import random
import time
from typing import TYPE_CHECKING
import logging

import config
from config import (
    configure_logging,
)

from rabbit.common import PaintButtonsRabbit

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

log = logging.getLogger(__name__)


def can_solve() -> bool:
    """
    Вероятность успеха не более 20%
    """
    return random.random() < 0.2


def extract_deaths_count(
    headers: dict[str, list[dict[str, int]]] | None,
) -> int:
    if headers and headers.get("x-death"):
        for props in headers["x-death"]:
            if "count" in props:
                return int(props["count"])
    return 0


def process_new_paint_button_task(
    ch: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    log.debug("ch: %s", ch)
    log.debug("method: %s", method)
    log.debug("properties: %s", properties)
    log.debug("body: %s", body)

    deaths_count = extract_deaths_count(properties.headers)
    log.warning("[⌛] Start painting %r, deaths %d", body, deaths_count)
    time.sleep(0.5)

    if can_solve():
        log.warning("[✅] Solved task %r after %d retries", body, deaths_count)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if deaths_count < 5:
        log.warning("[❌] Failed to paint button! %r deaths %d", body, deaths_count)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    # log.warning("[💀] Get rid of task %r after %d retries", body, deaths_count)
    # ch.basic_ack(delivery_tag=method.delivery_tag)
    log.warning("[✋] Delay task %r after %d retries for retro", body, deaths_count)
    ch.basic_publish(
        exchange=config.MQ_EXCHANGE,
        routing_key=config.MQ_QUEUE_NAME_NOT_SOLVED_PAINT_BUTTON_TASKS,
        body=body,
        properties=properties,
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    configure_logging(level=logging.INFO)
    with PaintButtonsRabbit() as rabbit:
        rabbit.consume_messages(message_callback=process_new_paint_button_task)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
