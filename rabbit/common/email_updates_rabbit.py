import logging
from typing import TYPE_CHECKING, Callable

from pika.exchange_type import ExchangeType

import config
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


log = logging.getLogger(__name__)


class EmailUpdatesRabbitMixin:
    channel: "BlockingChannel"

    def declare_email_updates_exchange(self) -> None:
        self.channel.exchange_declare(
            exchange=config.MQ_EMAIL_UPDATES_EXCHANGE_NAME,
            exchange_type=ExchangeType.fanout,
        )

    def declare_queue_for_email_updates(
        self,
        queue_name: str = "",
        exclusive: bool = True,
    ) -> str:
        self.declare_email_updates_exchange()
        queue = self.channel.queue_declare(
            queue=queue_name,
            exclusive=exclusive,
        )
        q_name = queue.method.queue
        self.channel.queue_bind(
            exchange=config.MQ_EMAIL_UPDATES_EXCHANGE_NAME,
            queue=q_name,
        )
        return q_name

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
        queue_name: str = "",
        prefetch_count: int = 1,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        q_name = self.declare_queue_for_email_updates(
            queue_name=queue_name,
            exclusive=not queue_name,
        )
        self.channel.basic_consume(
            queue=q_name,
            on_message_callback=message_callback,
        )
        log.warning("Waiting for messages...")
        self.channel.start_consuming()


class EmailUpdatesRabbit(EmailUpdatesRabbitMixin, RabbitBase):
    pass
