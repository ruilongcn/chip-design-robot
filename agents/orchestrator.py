# -*- coding: utf-8 -*-
"""Orchestrator：芯片设计多智能体流水线编排器。"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List

from . import chip_architect, rtl_designer, verification, eda_flow, tapeout_test, soc_coord

logger = logging.getLogger(__name__)

AGENT_REGISTRY = {
    "chip_architect": (chip_architect.ChipArchitectAgent, "芯片架构设计"),
    "rtl_designer": (rtl_designer.RTLDesignerAgent, "RTL 设计（Verilog/SystemVerilog）"),
    "verification": (verification.VerificationAgent, "验证（UVM/覆盖率/形式验证）"),
    "eda_flow": (eda_flow.EDAFlowAgent, "综合/布局布线（EDA）"),
    "tapeout_test": (tapeout_test.TapeoutTestAgent, "流片与封装测试"),
    "soc_coord": (soc_coord.SocCoordAgent, "芯片与指令集/BIOS/OS 协同"),
}


class Orchestrator:
    def __init__(self, llm_gateway=None, data_dir=None):
        self.llm_gateway = llm_gateway
        self.data_dir = data_dir
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def plan(self, goal: str) -> List[Dict[str, Any]]:
        g = goal.lower()
        plan: List[Dict[str, Any]] = []
        if any(k in g for k in ["架构", "微架构", "arch", "microarch", "ppa"]):
            plan.append({"agent": "chip_architect", "action": "arch", "params": {}})
        if any(k in g for k in ["rtl", "verilog", "systemverilog", "代码", "module"]):
            plan.append({"agent": "rtl_designer", "action": "module", "params": {}})
        if any(k in g for k in ["验证", "uvm", "覆盖率", "verify"]):
            plan.append({"agent": "verification", "action": "plan", "params": {}})
        if any(k in g for k in ["综合", "布局", "eda", "时序", "synth"]):
            plan.append({"agent": "eda_flow", "action": "synth", "params": {}})
        if any(k in g for k in ["流片", "封装", "测试", "tapeout", "package", "ate"]):
            plan.append({"agent": "tapeout_test", "action": "tapeout", "params": {}})
        if any(k in g for k in ["协同", "soc", "集成", "启动链", "生态"]):
            plan.append({"agent": "soc_coord", "action": "soc", "params": {}})
        if not plan:
            plan = [{"agent": "chip_architect", "action": "arch", "params": {}},
                    {"agent": "rtl_designer", "action": "module", "params": {}},
                    {"agent": "verification", "action": "plan", "params": {}},
                    {"agent": "eda_flow", "action": "synth", "params": {}},
                    {"agent": "tapeout_test", "action": "tapeout", "params": {}},
                    {"agent": "soc_coord", "action": "soc", "params": {}}]
        return plan

    def execute(self, goal: str, plan: List[Dict[str, Any]], params: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        for step in plan:
            agent_name = step["agent"]
            agent_cls, _ = AGENT_REGISTRY[agent_name]
            agent = agent_cls(config={}, data_dir=self.data_dir)
            task = dict(step.get("params", {}))
            task.update(params)
            task["action"] = step.get("action", "default")
            try:
                res = agent.run(task)
                results.append({"agent": agent_name, "ok": True, "result": res})
            except Exception as exc:  # noqa: BLE001
                logger.exception("Agent %s 失败", agent_name)
                results.append({"agent": agent_name, "ok": False, "error": str(exc)})
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        report = {"task_id": task_id, "goal": goal, "plan": plan, "results": results,
                  "status": "done", "created_at": __import__("time").time()}
        self._tasks[task_id] = report
        return report

    def run(self, goal: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        params = params or {}
        plan = self.plan(goal)
        return self.execute(goal, plan, params)

    def get_task(self, task_id: str) -> Dict[str, Any] | None:
        return self._tasks.get(task_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        return [{"name": name, "description": desc, "action_hint": self._hint(name)}
                for name, (cls, desc) in AGENT_REGISTRY.items()]

    def _hint(self, name: str) -> str:
        hints = {"chip_architect": "arch / microarch / ppa",
                 "rtl_designer": "module / code / lint",
                 "verification": "plan / uvm / cov",
                 "eda_flow": "synth / pnr / dft",
                 "tapeout_test": "tapeout / package / test",
                 "soc_coord": "soc / boot / ecosystem"}
        return hints.get(name, "")
