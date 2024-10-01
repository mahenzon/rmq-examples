import logging
from typing import TYPE_CHECKING, Callable

from pika.exchange_type import ExchangeType

import config
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


log = logging.getLogger(__name__)


class SimpleRabbitMixin:
    channel: "BlockingChannel"

    def declare_queue(self) -> None:
        self.channel.exchange_declare(
            exchange=config.MQ_NEWS_SIMPLE_DEAD_LETTER_EXCHANGE,
            exchange_type=ExchangeType.fanout,
        )
        dlq = self.channel.queue_declare(
            queue=config.MQ_NEWS_SIMPLE_DEAD_LETTER_KEY,
        )
        self.channel.queue_bind(
            queue=dlq.method.queue,
            exchange=config.MQ_NEWS_SIMPLE_DEAD_LETTER_EXCHANGE,
        )
        log.info("Declared dlq: %r", dlq.method.queue)

        queue = self.channel.queue_declare(
            queue=config.MQ_ROUTING_KEY,
            arguments={
                "x-dead-letter-exchange": config.MQ_NEWS_SIMPLE_DEAD_LETTER_EXCHANGE,
            },
        )
        log.info("Declared queue: %r", queue.method.queue)

    def consume_messages(
        self,
        message_callback: Callable[
            [
                "BlockingChannel",
                "Basic.Deliver",
                "BasicProperties",
                bytes,
            ],
            None,
        ],
        prefetch_count: int = 1,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue()
        self.channel.basic_consume(
            queue=config.MQ_ROUTING_KEY,
            on_message_callback=message_callback,
        )
        log.warning("Waiting for messages...")
        self.channel.start_consuming()


class SimpleRabbit(SimpleRabbitMixin, RabbitBase):
    pass
