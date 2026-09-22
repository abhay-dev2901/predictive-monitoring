import random
import time

import requests

BASE_URL = "http://localhost:8000"

while True:
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)

        requests.get(f"{BASE_URL}/products", timeout=2)

        if random.random() < 0.6:
            product_id = random.choice([1, 2, 3])
            quantity = random.randint(1, 3)

            requests.post(
                f"{BASE_URL}/orders",
                json={
                    "product_id": product_id,
                    "quantity": quantity,
                },
                timeout=2,
            )

        if random.random() < 0.05:
            requests.get(f"{BASE_URL}/orders/999999", timeout=2)

        time.sleep(random.uniform(0.2, 1.0))

    except requests.RequestException as exc:
        print("Request failed:", exc)
        time.sleep(1)
