import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


def _load_module(module_name: str, relative_path: str):
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(module_name, root / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeChannel:
    def __init__(self, published_messages: list):
        self.published_messages = published_messages
        self.acked = []
        self.nacked = []

    def queue_declare(self, queue: str, durable: bool = False):
        self.queue = queue
        self.durable = durable

    def basic_publish(self, exchange: str, routing_key: str, body: str, properties=None):
        self.published_messages.append(
            {
                "exchange": exchange,
                "routing_key": routing_key,
                "body": body,
                "properties": properties,
            }
        )

    def basic_ack(self, delivery_tag: int):
        self.acked.append(delivery_tag)

    def basic_nack(self, delivery_tag: int, requeue: bool = False):
        self.nacked.append((delivery_tag, requeue))


class FakeConnection:
    def __init__(self, published_messages: list):
        self._channel = FakeChannel(published_messages)

    def channel(self):
        return self._channel

    def close(self):
        pass


def test_trace_propagates_from_producer_to_consumer(monkeypatch, span_exporter):
    published_messages = []

    producer_mod = _load_module("order_producer", "services/order-service/app/producers.py")
    consumer_mod = _load_module("order_consumer", "services/order-service/app/consumers.py")

    # ผูก tracer ของโมดูลเข้ากับ TracerProvider ที่ fixture ตั้งค่าไว้
    from opentelemetry import trace

    producer_mod.tracer = trace.get_tracer("order-service.producer")
    consumer_mod.tracer = trace.get_tracer("order-service.consumer")

    # แทนที่การเชื่อมต่อ RabbitMQ จริงด้วย FakeConnection
    monkeypatch.setattr(
        producer_mod.pika,
        "BlockingConnection",
        lambda params: FakeConnection(published_messages),
    )
    # ลดเวลา sleep ใน consumer เพื่อไม่ให้เทสต์ช้า
    monkeypatch.setattr(consumer_mod.time, "sleep", lambda _: None)

    order_payload = {"item_id": "item-999", "quantity": 2}
    ok = producer_mod.publish_order_event(order_payload)
    assert ok is True
    assert len(published_messages) == 1

    msg = published_messages[0]
    assert msg["properties"] is not None
    assert "traceparent" in msg["properties"].headers

    fake_channel = FakeChannel([])
    fake_method = SimpleNamespace(delivery_tag=42)
    consumer_mod.process_order_message(
        ch=fake_channel,
        method=fake_method,
        properties=msg["properties"],
        body=json.dumps(order_payload).encode("utf-8"),
    )

    assert fake_channel.acked == [42]
    assert fake_channel.nacked == []

    spans = span_exporter.get_finished_spans()
    by_name = {s.name: s for s in spans}

    assert "rabbitmq.publish_order" in by_name
    assert "rabbitmq.consume_order" in by_name

    producer_span = by_name["rabbitmq.publish_order"]
    consumer_span = by_name["rabbitmq.consume_order"]

    producer_ctx = producer_span.get_span_context()
    consumer_ctx = consumer_span.get_span_context()

    # 1. Trace ID ต้องเหมือนกันข้าม Producer และ Consumer
    assert producer_ctx.trace_id == consumer_ctx.trace_id
    # 2. Consumer Span ต้องมี Parent เป็น Producer Span
    assert consumer_span.parent is not None
    assert consumer_span.parent.span_id == producer_ctx.span_id
