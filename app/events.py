import json
import os
import time
from typing import Any

from confluent_kafka import Producer

from .metrics import ORDER_EVENTS_FAILED, ORDER_EVENTS_PUBLISHED

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
ORDER_EVENTS_TOPIC = os.getenv("ORDER_EVENTS_TOPIC", "orders")


class KafkaEventPublisher:
    def __init__(self) -> None:
        self.producer = Producer(
            {
                "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
                "client.id": "monitoring-api",
            }
        )

    def publish_order_created(self, event: dict[str, Any]) -> None:
        payload = json.dumps(event).encode("utf-8")
        key = str(event["order_id"]).encode("utf-8")

        try:
            try:
                self.producer.produce(
                    ORDER_EVENTS_TOPIC,
                    key=key,
                    value=payload,
                    on_delivery=self._delivery_callback,
                )
            except BufferError:
                self.producer.flush(5)
                self.producer.produce(
                    ORDER_EVENTS_TOPIC,
                    key=key,
                    value=payload,
                    on_delivery=self._delivery_callback,
                )

            self.producer.poll(0)
        except Exception:
            ORDER_EVENTS_FAILED.inc()
            raise

    def close(self) -> None:
        self.producer.flush(10)

    @staticmethod
    def _delivery_callback(error, message) -> None:
        if error is not None:
            ORDER_EVENTS_FAILED.inc()
            return

        ORDER_EVENTS_PUBLISHED.inc()


def build_order_created_event(
    *,
    order_id: int,
    product_id: int,
    quantity: int,
) -> dict[str, Any]:
    return {
        "event_type": "order.created",
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "created_at": time.time(),
    }
