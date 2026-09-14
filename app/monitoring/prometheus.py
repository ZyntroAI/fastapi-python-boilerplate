from prometheus_fastapi_instrumentator import Instrumentator, metrics

def setup_prometheus(app):
    Instrumentator()\
        .add(metrics.request_size())\
        .add(metrics.response_size())\
        .add(metrics.latency())\
        .add(metrics.requests())\
        .add(metrics.status_codes())\
        .instrument(app)\
        .expose(app)
