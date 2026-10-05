from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation"],
)

ORDERS_CREATED = Counter(
    "orders_created_total",
    "Total orders created",
)

ORDER_EVENTS_PUBLISHED = Counter(
    "order_events_published_total",
    "Total order events successfully published to Kafka",
)

ORDER_EVENTS_FAILED = Counter(
    "order_events_failed_total",
    "Total order events that failed to publish to Kafka",
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Current number of active HTTP requests",
)
