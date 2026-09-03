from __future__ import annotations
import asyncio
import json
import logging
from typing import Any, Callable, Coroutine
from app.core.config import get_settings
from app.models.schemas import KafkaStatus, SocialMediaPost

logger = logging.getLogger("updates.kafka")

RAW_TOPIC = "social-media-raw"
NORMALIZED_TOPIC = "social-media-normalized"
QUALIFIED_TOPIC = "social-media-qualified"

import socket

def _is_broker_listening(bootstrap: str) -> bool:
    try:
        parts = bootstrap.split(",")[0].strip().split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 9092
        with socket.create_connection((host, port), timeout=0.1):
            return True
    except (OSError, ValueError):
        return False

class KafkaStreamService:
    """Manages Apache Kafka streaming with real aiokafka producer/consumer."""
    _instance: KafkaStreamService | None = None

    def __init__(self):
        self.settings = get_settings()
        self.bootstrap_servers = self.settings.kafka_bootstrap_servers
        self.producer = None
        self.is_connected = False
        self.last_error: str | None = None
        self.mode = "initializing"
        self._memory_queue: asyncio.Queue = asyncio.Queue()
        self._consumers: list[Callable[[str, dict], Coroutine[Any, Any, None]]] = []
        self._running = False
        self._consumer_task: asyncio.Task | None = None

    @classmethod
    def get_instance(cls) -> KafkaStreamService:
        if cls._instance is None:
            cls._instance = KafkaStreamService()
        return cls._instance

    async def start(self) -> None:
        """Attempt connection to real Kafka broker at bootstrap_servers."""
        self._running = True
        if not _is_broker_listening(self.bootstrap_servers):
            self.is_connected = False
            self.producer = None
            self.mode = "in_memory_fallback_broker_pending"
            self.last_error = f"Kafka broker ({self.bootstrap_servers}) offline"
            if self._consumer_task is None:
                self._consumer_task = asyncio.create_task(self._process_memory_queue())
            return

        try:
            from aiokafka import AIOKafkaProducer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                request_timeout_ms=1000,
            )
            await asyncio.wait_for(self.producer.start(), timeout=1.0)
            self.is_connected = True
            self.mode = "broker_connected"
            self.last_error = None
            logger.info(f"Connected to Apache Kafka broker at {self.bootstrap_servers}")
        except Exception as exc:
            self.is_connected = False
            self.producer = None
            self.mode = "in_memory_fallback_broker_pending"
            self.last_error = f"Kafka broker ({self.bootstrap_servers}) offline: {exc}"

            logger.warning(
                f"Kafka broker not reachable at {self.bootstrap_servers}. "
                "Operating in in-memory streaming fallback mode. Start docker-compose up -d kafka to enable full broker streaming."
            )

        # Start consumer loop for internal subscribers
        if self._consumer_task is None:
            self._consumer_task = asyncio.create_task(self._process_memory_queue())

    async def stop(self) -> None:
        self._running = False
        if self.producer:
            try:
                await self.producer.stop()
            except Exception:
                pass
        if self._consumer_task:
            self._consumer_task.cancel()
            self._consumer_task = None

    def register_consumer(self, handler: Callable[[str, dict], Coroutine[Any, Any, None]]) -> None:
        self._consumers.append(handler)

    async def publish_raw(self, platform: str, payload: dict) -> None:
        await self._publish(RAW_TOPIC, {"platform": platform, "raw": payload})

    async def publish_normalized(self, post: SocialMediaPost) -> None:
        await self._publish(NORMALIZED_TOPIC, post.model_dump(mode="json"))

    async def publish_qualified(self, qualified_payload: dict) -> None:
        await self._publish(QUALIFIED_TOPIC, qualified_payload)

    async def _publish(self, topic: str, data: dict) -> None:
        if self.is_connected and self.producer:
            try:
                payload_bytes = json.dumps(data).encode("utf-8")
                await self.producer.send_and_wait(topic, payload_bytes)
                logger.debug(f"Pushed record to Kafka topic '{topic}'")
                return
            except Exception as exc:
                self.is_connected = False
                self.mode = "in_memory_fallback_broker_pending"
                self.last_error = f"Broker connection lost while sending to {topic}: {exc}"
                logger.warning(f"Kafka send failed, routing to local streaming queue: {exc}")

        # In-memory queue fallback
        await self._memory_queue.put((topic, data))

    async def _process_memory_queue(self) -> None:
        while self._running:
            try:
                topic, data = await self._memory_queue.get()
                for handler in self._consumers:
                    try:
                        await handler(topic, data)
                    except Exception as e:
                        logger.error(f"Error in streaming subscriber for topic {topic}: {e}")
                self._memory_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Error in stream processor: {exc}")
                await asyncio.sleep(0.1)

    def get_status(self) -> KafkaStatus:
        message = (
            f"Connected to Kafka broker at {self.bootstrap_servers}. Active topics: {RAW_TOPIC}, {NORMALIZED_TOPIC}, {QUALIFIED_TOPIC}."
            if self.is_connected
            else f"Broker offline at {self.bootstrap_servers} ({self.last_error or 'Connection pending'}). Running via async streaming queue. Start Docker Compose or configure KAFKA_BOOTSTRAP_SERVERS to connect external cluster."
        )
        return KafkaStatus(
            connected=self.is_connected,
            bootstrap_servers=self.bootstrap_servers,
            topics=[RAW_TOPIC, NORMALIZED_TOPIC, QUALIFIED_TOPIC],
            mode=self.mode,
            message=message,
        )

def get_kafka_service() -> KafkaStreamService:
    return KafkaStreamService.get_instance()
