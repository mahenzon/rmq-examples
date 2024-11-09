import logging
from typing import TYPE_CHECKING, Callable

import config
from rabbit.base import RabbitBase

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


log = logging.getLogger(__name__)


class WeatherRabbitMixin:
    channel: "BlockingChannel"

    def publish_message(
        self,
        text: str,
        exchange: str = config.MQ_EXCHANGE,
        routing_key: str = config.MQ_QUEUE_NAME_WEATHER_UPDATES,
    ) -> None:
        log.info("Publish message %r", text)
        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=text,
        )
        log.warning("Published message %r", text)

    def declare_queue(self) -> None:
        dlq = self.channel.queue_declare(
            queue=config.MQ_DLQ_NAME_EXPIRED_WEATHER_UPDATES,
            arguments={
                "x-message-ttl": config.MQ_DLQ_EXPIRED_WEATHER_UPDATES_TTL,
            },
        )
        log.warning("Declared dlq %r", dlq.method.queue)

        weather_queue = self.channel.queue_declare(
            queue=config.MQ_QUEUE_NAME_WEATHER_UPDATES,
            arguments={
                "x-message-ttl": config.MQ_QUEUE_WEATHER_UPDATES_TTL,
                "x-dead-letter-exchange": config.MQ_EXCHANGE,
                "x-dead-letter-routing-key": config.MQ_DLQ_NAME_EXPIRED_WEATHER_UPDATES,
            },
        )
        log.warning(
            "Declared weather queue %r",
            weather_queue.method.queue,
        )

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
        queue_name: str = config.MQ_QUEUE_NAME_WEATHER_UPDATES,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue()
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_callback,
        )
        log.warning("Waiting for messages...")
        self.channel.start_consuming()


class WeatherRabbit(WeatherRabbitMixin, RabbitBase):
    pass
