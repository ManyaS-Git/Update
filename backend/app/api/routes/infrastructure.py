from __future__ import annotations

import importlib.util
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.models.database import engine
from app.services.streaming import event_bus

router=APIRouter(prefix="/api/infrastructure",tags=["infrastructure"])


@router.get("/status")
def infrastructure_status():
    settings=get_settings()
    try:
        with engine.connect() as connection:connection.execute(text("SELECT 1"))
        database={"connected":True,"backend":engine.url.get_backend_name(),"error":None}
    except Exception as exc:database={"connected":False,"backend":engine.url.get_backend_name(),"error":str(exc)}
    return {"database":database,"kafka":event_bus.status(),"models":{"transformers":bool(importlib.util.find_spec("transformers")),"torch":bool(importlib.util.find_spec("torch")),"networkx":bool(importlib.util.find_spec("networkx")),"bertopic":bool(importlib.util.find_spec("bertopic")),"torch_geometric":bool(importlib.util.find_spec("torch_geometric")),"sarcasm_endpoint_configured":bool(settings.sarcasm_inference_endpoint_url)},"readiness":{"direct_pipeline":database["connected"],"streaming_pipeline":database["connected"] and event_bus.connected,"graphsage":bool(importlib.util.find_spec("torch_geometric")),"sarcasm":bool(settings.sarcasm_inference_endpoint_url)}}
