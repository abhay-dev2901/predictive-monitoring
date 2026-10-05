import json
import os
import signal
from typing import Any

from confluent_kafka import Consumer, KafkaException

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
ORDER_EVENTS_TOPIC = os.getenv("ORDER_EVENTS_TOPIC", "orders")

running = True


def shutdown_handler(signum, frame) -> None:
    global running
    running = False


def handle_order_event(event: dict[str, Any]) -> None:
    print(
        "order event received:",
        {
            "event_type": event.get("event_type"),
            "order_id": event.get("order_id"),
            "product_id": event.get("product_id"),
            "quantity": event.get("quantity"),
        },
        flush=True,
    )


def main() -> None:
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "order-event-consumer",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )
    consumer.subscribe([ORDER_EVENTS_TOPIC])

    print(f"listening for Kafka events on topic {ORDER_EVENTS_TOPIC}", flush=True)

    try:
        while running:
            message = consumer.poll(1.0)
            if message is None:
                continue

            if message.error():
                raise KafkaException(message.error())

            event = json.loads(message.value().decode("utf-8"))
            handle_order_event(event)
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
