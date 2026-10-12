# -*- coding: utf-8 -*-
"""芯片设计智能体团队 - FastAPI 后端入口。

启动：python scripts/start_backend.py（默认 http://127.0.0.1:8004）
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.orchestrator import Orchestrator  # noqa: E402
from services.llm_gateway import LLMGateway  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("chip-web")

app = FastAPI(title="芯片设计智能体团队", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

llm = LLMGateway(config_dir=ROOT / "config")
orch = Orchestrator(llm_gateway=llm, data_dir=DATA_DIR)

STATIC_DIR = ROOT / "web" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "chip-design-agent-team", "llm": llm.stats()}


@app.get("/api/agents")
def agents():
    return {"agents": orch.list_agents()}


@app.post("/api/tasks")
def create_task(body: dict):
    goal = body.get("goal", "设计自主芯片并完成协同")
    params = body.get("params", {})
    return orch.run(goal, params)


@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    report = orch.get_task(task_id)
    if report is None:
        return {"error": "task not found"}
    return report


@app.get("/api/contracts/{sub_dir}")
def list_contracts(sub_dir: str):
    target = DATA_DIR / sub_dir
    if not target.exists():
        return {"items": []}
    items = []
    for f in sorted(target.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:50]:
        items.append({"name": f.name, "path": str(f), "mtime": int(f.stat().st_mtime)})
    return {"items": items}
