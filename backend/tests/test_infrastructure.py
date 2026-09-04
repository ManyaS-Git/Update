import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.services.streaming import KafkaEventBus

client=TestClient(app)


def test_infrastructure_status_is_honest_and_direct_pipeline_stays_ready():
    payload=client.get("/api/infrastructure/status").json()
    assert payload["database"]["connected"] is True
    assert payload["readiness"]["direct_pipeline"] is True
    assert payload["kafka"]["enabled"] is False
    assert payload["readiness"]["streaming_pipeline"] is False
    assert payload["readiness"]["sarcasm"] is False


def test_disabled_kafka_bus_is_a_real_noop_not_fake_delivery():
    bus=KafkaEventBus()
    asyncio.run(bus.publish("unused",{"event_id":"test"},"test"))
    assert bus.published==0 and bus.connected is False


def test_sarcasm_is_unavailable_without_validated_endpoint():
    payload=client.post("/api/classify",json={"text":"Oh great, another three-hour traffic jam."}).json()
    assert payload["sarcasm_detected"] is None
    assert payload["sarcasm_confidence"] is None
    assert payload["sarcasm_model_name"] is None
    assert "unavailable" in payload["evidence"]["sarcasm"][0]

