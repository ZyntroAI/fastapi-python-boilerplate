# Install locust
pip install locust

# Run a simple load test (locustfile.py)
from locust import HttpUser, task

class FastAPIUser(HttpUser):
    @task
    def get_items(self):
        self.client.get("/v1/items/1")
