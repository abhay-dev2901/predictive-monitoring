# Predictive Observability Platform — Phase 2

This project is moving through a larger observability roadmap:

**Real-time monitoring → anomaly detection → time-series forecasting → incident prediction → AI investigation**

## Current Goal

Build a working monitoring and event-streaming foundation with:

- FastAPI application
- PostgreSQL
- Docker Compose
- Prometheus metrics
- Grafana
- Synthetic traffic
- Kafka event streaming
- Order event consumer

No ML yet. Phase 2 focuses on separating business writes from downstream event processing.

## Architecture

```text
Synthetic traffic
  -> FastAPI API
  -> PostgreSQL
  -> Kafka topic: orders
  -> Order consumer

Prometheus
  -> scrapes FastAPI /metrics
  -> Grafana dashboards
```

When an order is created:

1. FastAPI validates the request.
2. The order is committed to PostgreSQL.
3. The app publishes an `order.created` event to Kafka.
4. The order consumer reads the event from Kafka.
5. Prometheus tracks request, database, order, and Kafka publish metrics.

## Run

```bash
docker compose up --build
```

Open:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Kafka external listener: localhost:9094

Grafana default login:

```text
username: admin
password: admin
```

## Generate Traffic

In another terminal:

```bash
cd scripts
python3 -m pip install -r requirements.txt
python3 generate_traffic.py
```

Leave it running so Prometheus has telemetry to collect.

## Watch Kafka Events

The `order-consumer` service logs every order event it receives:

```bash
docker compose logs -f order-consumer
```

You can also inspect the app logs:

```bash
docker compose logs -f app
```

## Useful Prometheus queries

Request rate:

```promql
rate(http_requests_total[1m])
```

P95 latency:

```promql
histogram_quantile(
  0.95,
  sum(rate(http_request_duration_seconds_bucket[5m]))
  by (le)
)
```

Error rate:

```promql
sum(rate(http_requests_total{status=~"4..|5.."}[1m]))
/
sum(rate(http_requests_total[1m]))
```

Active requests:

```promql
http_active_requests
```

Orders created:

```promql
rate(orders_created_total[1m])
```

Kafka order events published:

```promql
rate(order_events_published_total[1m])
```

Kafka publish failures:

```promql
rate(order_events_failed_total[1m])
```

Database latency:

```promql
rate(db_query_duration_seconds_sum[5m])
/
rate(db_query_duration_seconds_count[5m])
```

## What we learn in Phase 1

- Health checks
- Structured application metrics
- Request latency measurement
- Database monitoring
- Prometheus scraping
- Grafana visualization
- Docker networking
- Basic production-style observability

## What we learn in Phase 2

- Kafka broker setup
- Topic-based event streaming
- Producer/consumer separation
- Event-driven architecture
- Decoupling API writes from downstream processing
- Metrics for event publishing success and failure

## Next Phase

After this works:

**Phase 3 → anomaly detection**

We will use the monitoring metrics and order event stream as inputs for detecting unusual system or business behavior.
