from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from typing import Any

from app.core.config import Settings, get_settings


class KafkaUnavailable(RuntimeError):
    pass


class KafkaEventBus:
    """Real Kafka producer with an explicit disabled state; never simulates delivery."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._producer = None
        self.last_error: str | None = None
        self.published = 0

    @property
    def enabled(self) -> bool:
        return self.settings.kafka_enabled

    @property
    def connected(self) -> bool:
        return self._producer is not None

    async def start(self) -> None:
        if not self.enabled:
            return
        if not importlib.util.find_spec("aiokafka"):
            self.last_error="KAFKA_ENABLED=true requires the infrastructure dependencies (aiokafka)"
            raise KafkaUnavailable("KAFKA_ENABLED=true requires the infrastructure dependencies (aiokafka)")
        from aiokafka import AIOKafkaProducer

        kwargs: dict[str, Any] = {
            "bootstrap_servers": self.settings.kafka_bootstrap_servers,
            "client_id": self.settings.kafka_client_id,
            "acks": "all",
            "enable_idempotence": True,
            "compression_type": "gzip",
            "value_serializer": lambda value: json.dumps(value, default=str, separators=(",", ":")).encode(),
            "security_protocol": self.settings.kafka_security_protocol,
        }
        if self.settings.kafka_security_protocol.startswith("SASL"):
            if not self.settings.kafka_sasl_username or not self.settings.kafka_sasl_password:
                self.last_error="Kafka SASL is enabled but username/password are missing"
                raise KafkaUnavailable("Kafka SASL is enabled but username/password are missing")
            kwargs.update(sasl_mechanism=self.settings.kafka_sasl_mechanism,sasl_plain_username=self.settings.kafka_sasl_username,sasl_plain_password=self.settings.kafka_sasl_password)
        producer=AIOKafkaProducer(**kwargs)
        try:
            await producer.start()
        except Exception as exc:
            self.last_error=str(exc)
            raise KafkaUnavailable(f"Kafka connection failed: {exc}") from exc
        self._producer=producer;self.last_error=None

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop();self._producer=None

    async def publish(self, topic: str, payload: dict, key: str | None = None) -> None:
        if not self.enabled:
            return
        if self._producer is None:
            raise KafkaUnavailable("Kafka is enabled but the producer is not connected")
        envelope={"schema_version":1,"event_id":payload.get("event_id"),"emitted_at":datetime.now(timezone.utc).isoformat(),"payload":payload}
        try:
            await self._producer.send_and_wait(topic,envelope,key=key.encode() if key else None);self.published+=1;self.last_error=None
        except Exception as exc:
            self.last_error=str(exc)
            try:
                await self._producer.send_and_wait(self.settings.kafka_dead_letter_topic,{**envelope,"failed_topic":topic,"error":str(exc)},key=key.encode() if key else None)
            except Exception:
                pass
            raise

    def status(self) -> dict:
        return {"enabled":self.enabled,"connected":self.connected,"client_installed":bool(importlib.util.find_spec("aiokafka")),"bootstrap_servers_configured":bool(self.settings.kafka_bootstrap_servers),"published_events":self.published,"last_error":self.last_error,"topics":{"raw":self.settings.kafka_raw_topic,"normalized":self.settings.kafka_normalized_topic,"qualified":self.settings.kafka_qualified_topic,"dead_letter":self.settings.kafka_dead_letter_topic}}


event_bus=KafkaEventBus()
