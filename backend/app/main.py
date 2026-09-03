from contextlib import asynccontextmanager, suppress
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.analysis import router as analysis_router
from app.api.routes.topics import router as topics_router
from app.api.routes.content import router as content_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.insights import router as insights_router
from app.core.config import get_settings
from app.services.database import init_database, bootstrap_live_data
from app.services.auto_ingestion import auto_ingestion_loop
from app.services.kafka_stream import get_kafka_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("updates.main")

settings = get_settings()
init_database()

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Initializing updates database...")
    init_database()

    asyncio.create_task(asyncio.to_thread(bootstrap_live_data))

    kafka = get_kafka_service()
    if settings.kafka_enabled:
        logger.info("Starting Apache Kafka streaming layer...")
        await kafka.start()

    task = asyncio.create_task(auto_ingestion_loop()) if settings.auto_ingestion_enabled else None


    try:
        yield
    finally:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        if settings.kafka_enabled:
            await kafka.stop()

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="Real-Time Evidence-Backed Social Media Analytics Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics_router)
app.include_router(content_router)
app.include_router(intelligence_router)
app.include_router(analysis_router)
app.include_router(insights_router)

@app.get("/health")
def health():
    kafka_status = get_kafka_service().get_status()
    return {
        "status": "ok",
        "demo_mode": settings.demo_mode,
        "kafka_connected": kafka_status.connected,
        "kafka_mode": kafka_status.mode,
    }
