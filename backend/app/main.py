from contextlib import asynccontextmanager
import asyncio
from contextlib import suppress
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.analysis import router as analysis_router
from app.api.routes.topics import router as topics_router
from app.api.routes.content import router as content_router
from app.api.routes.intelligence import router as intelligence_router
from app.core.config import get_settings
from app.services.database import init_database
from app.services.auto_ingestion import auto_ingestion_loop

settings=get_settings()
init_database()

@asynccontextmanager
async def lifespan(_:FastAPI):
    init_database()
    task=asyncio.create_task(auto_ingestion_loop()) if settings.auto_ingestion_enabled else None
    try:yield
    finally:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):await task

app=FastAPI(title=settings.app_name,version="1.0.0",description="Evidence-backed public conversation intelligence platform",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(topics_router);app.include_router(content_router);app.include_router(intelligence_router);app.include_router(analysis_router)

@app.get("/health")
def health(): return {"status":"ok","demo_mode":settings.demo_mode}
