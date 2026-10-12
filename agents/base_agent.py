# -*- coding: utf-8 -*-
"""通用智能体基类。"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict


class BaseAgent:
    """所有专业 Agent 的基类：统一契约落盘、LLM 网关接入、工具命名空间。"""

    name = "base"
    description = ""

    def __init__(self, config: Dict[str, Any] | None = None, data_dir: str | Path | None = None):
        self.config = config or {}
        self.data_dir = Path(data_dir) if data_dir else Path("data")
        self.sub_dir = self.data_dir / self.name
        self.sub_dir.mkdir(parents=True, exist_ok=True)

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """子类覆写：接收任务字典，返回结果字典。"""
        raise NotImplementedError

    # ---- 工具 ----
    def save_contract(self, payload: Dict[str, Any], prefix: str = "") -> str:
        """保存产出契约到 data/<agent>/ 目录，返回相对文件名。"""
        ts = time.strftime("%Y%m%d_%H%M%S")
        fname = f"{prefix}_{ts}_{uuid.uuid4().hex[:6]}.json" if prefix else f"{ts}_{uuid.uuid4().hex[:6]}.json"
        path = self.sub_dir / fname
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(path)

    def load_contracts(self, limit: int = 20) -> list[dict]:
        files = sorted(self.sub_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        out = []
        for f in files:
            try:
                out.append({"file": f.name, "path": str(f), "data": json.loads(f.read_text(encoding="utf-8"))})
            except Exception:
                out.append({"file": f.name, "path": str(f), "data": {}})
        return out

    def llm(self, prompt: str, system: str = "") -> str:
        """通过网关调用 LLM；无凭据/失败时返回空串，由规则引擎兜底。"""
        gateway = self.config.get("llm_gateway")
        if gateway is None:
            return ""
        return gateway.complete(prompt, system=system)

    def _mk(self, **kwargs: Any) -> Dict[str, Any]:
        return {"agent": self.name, "ts": time.time(), **kwargs}
