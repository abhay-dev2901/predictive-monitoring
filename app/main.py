import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from .database import Base, SessionLocal, engine, get_db
from .metrics import (
    ACTIVE_REQUESTS,
    DB_QUERY_LATENCY,
    ORDERS_CREATED,
    REQUEST_COUNT,
    REQUEST_LATENCY,
)
from .models import Order, Product


class OrderRequest(BaseModel):
    product_id: int
    quantity: int


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        ACTIVE_REQUESTS.inc()

        try:
            response = await call_next(request)
            status = str(response.status_code)
            return response
        except Exception:
            status = "500"
            raise
        finally:
            duration = time.perf_counter() - start
            path = request.url.path
            method = request.method

            REQUEST_COUNT.labels(
                method=method,
                path=path,
                status=status,
            ).inc()

            REQUEST_LATENCY.labels(
                method=method,
                path=path,
            ).observe(duration)

            ACTIVE_REQUESTS.dec()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Seed data only when the table is empty.
    with SessionLocal() as db:
        existing = db.scalar(select(Product).limit(1))
        if existing is None:
            db.add_all(
                [
                    Product(name="Keyboard", price=2500),
                    Product(name="Mouse", price=1200),
                    Product(name="Monitor", price=15000),
                ]
            )
            db.commit()

    yield


app = FastAPI(
    title="Predictive Monitoring Demo",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(MetricsMiddleware)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    start = time.perf_counter()
    products = db.scalars(select(Product)).all()
    DB_QUERY_LATENCY.labels(operation="get_products").observe(
        time.perf_counter() - start
    )

    return products


@app.post("/orders")
def create_order(order: OrderRequest, db: Session = Depends(get_db)):
    if order.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0",
        )

    start = time.perf_counter()
    product = db.get(Product, order.product_id)
    DB_QUERY_LATENCY.labels(operation="get_product").observe(
        time.perf_counter() - start
    )

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    new_order = Order(
        product_id=order.product_id,
        quantity=order.quantity,
    )

    start = time.perf_counter()
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    DB_QUERY_LATENCY.labels(operation="create_order").observe(
        time.perf_counter() - start
    )

    ORDERS_CREATED.inc()

    return {
        "id": new_order.id,
        "product_id": new_order.product_id,
        "quantity": new_order.quantity,
    }


@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    start = time.perf_counter()
    order = db.get(Order, order_id)
    DB_QUERY_LATENCY.labels(operation="get_order").observe(
        time.perf_counter() - start
    )

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
