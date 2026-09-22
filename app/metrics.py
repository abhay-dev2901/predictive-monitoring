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

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Current number of active HTTP requests",
)
