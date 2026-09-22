# Predictive Observability Platform — Phase 1

This is the first step of a larger project:

**Real-time monitoring → anomaly detection → time-series forecasting → incident prediction → AI investigation**

## Phase 1 Goal

Build a working monitoring foundation with:

- FastAPI application
- PostgreSQL
- Docker Compose
- Prometheus metrics
- Grafana
- Synthetic traffic

No Kafka and no ML yet.

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

## Next Phase

After this works:

**Phase 2 → Kafka + event streaming**

We will not add Kafka until this basic monitoring pipeline is working.
