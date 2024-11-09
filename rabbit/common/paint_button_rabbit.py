import logging
from typing import TYPE_CHECKING, Callable

from pika.exchange_type import ExchangeType

import config
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


log = logging.getLogger(__name__)


class PaintButtonsRabbitMixin:
    channel: "BlockingChannel"

    def publish_message(
        self,
        text: str,
        exchange: str = config.MQ_EXCHANGE_PAINT_BUTTON_TASKS,
        routing_key: str = config.MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
    ) -> None:
        log.info("Publish message %r", text)
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=text,
        )
        log.warning("Published message %r", text)

    def declare_last_resort_queue(self) -> str:
        queue = self.channel.queue_declare(
            queue=config.MQ_QUEUE_NAME_NOT_SOLVED_PAINT_BUTTON_TASKS,
        )
        log.warning("Declared last resort queue %r", queue.method.queue)
        return queue.method.queue

    def declare_dlq(self) -> str:
        self.channel.exchange_declare(
            exchange=config.MQ_DLX_NAME_FAILED_TO_PAINT_BUTTON_TASKS,
            exchange_type=ExchangeType.fanout,
        )
        dlq = self.channel.queue_declare(
            queue=config.MQ_DLQ_NAME_FAILED_TO_PAINT_BUTTON_TASKS,
            arguments={
                # TTL in milliseconds
                "x-message-ttl": config.MQ_FAILED_TO_PAINT_BUTTON_TASKS_RETRY_IN_SECONDS
                * 1000,
                "x-dead-letter-exchange": config.MQ_EXCHANGE_PAINT_BUTTON_TASKS,
                "x-dead-letter-routing-key": config.MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
            },
        )
        self.channel.queue_bind(
            queue=dlq.method.queue,
            exchange=config.MQ_DLX_NAME_FAILED_TO_PAINT_BUTTON_TASKS,
        )
        log.warning("Declared dlq %r", dlq.method.queue)
        return dlq.method.queue

    def declare_main_queue(self) -> str:
        self.channel.exchange_declare(
            exchange=config.MQ_EXCHANGE_PAINT_BUTTON_TASKS,
            exchange_type=ExchangeType.direct,
        )
        main_queue = self.channel.queue_declare(
            queue=config.MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
            arguments={
                "x-dead-letter-exchange": config.MQ_DLX_NAME_FAILED_TO_PAINT_BUTTON_TASKS,
            },
        )
        self.channel.queue_bind(
            queue=main_queue.method.queue,
            exchange=config.MQ_EXCHANGE_PAINT_BUTTON_TASKS,
        )
        log.warning(
            "Declared paint button tasks queue %r",
            main_queue.method.queue,
        )
        return main_queue.method.queue

    def declare_queue(self) -> None:
        self.declare_last_resort_queue()
        self.declare_dlq()
        self.declare_main_queue()

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
        queue_name: str = config.MQ_QUEUE_NAME_PAINT_BUTTON_TASKS,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue()
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_callback,
        )
        log.warning("Waiting for paint button tasks...")
        self.channel.start_consuming()


class PaintButtonsRabbit(PaintButtonsRabbitMixin, RabbitBase):
    pass
