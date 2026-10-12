# -*- coding: utf-8 -*-
"""流片与封装测试 Agent：晶圆流片、封装设计、ATE 测试、可靠性。"""
from __future__ import annotations

from typing import Any, Dict

from .base_agent import BaseAgent


class TapeoutTestAgent(BaseAgent):
    name = "tapeout_test"
    description = "流片测试工程师：流片签核、封装设计、ATE 测试、可靠性评估"

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "tapeout")
        if action == "tapeout":
            return self._tapeout(task)
        if action == "package":
            return self._package(task)
        if action == "test":
            return self._test(task)
        return self._tapeout(task)

    def _tapeout(self, task):
        payload = {
            "stage": "流片签核清单",
            "checklist": ["RTL freeze + 门级网表签核", "时序/功耗/面积签核", "DRC/LVS clean", "DFT 覆盖率达标", "物理验证 signoff", "GDSII 交付"],
            "foundry_consideration": "国内代工优先（自主可控供应链），多源备选",
            "risk": "掩膜/流片周期与成本、良率爬坡",
        }
        path = self.save_contract(payload, "tapeout")
        return self._mk(action="tapeout", result=payload, contract=path)

    def _package(self, task):
        payload = {
            "topic": "封装设计",
            "options": ["QFP/LQFP（低成本）", "BGA（高密度）", "Chiplet/2.5D（先进封装）"],
            "thermal": "封装热阻评估、散热方案",
            "pinout": "与主板适配协同 openbios/mainboard_adapt",
            "note": "封装选择影响整机成本与散热，与 computer fixer 整机方案联动。",
        }
        path = self.save_contract(payload, "package")
        return self._mk(action="package", result=payload, contract=path)

    def _test(self, task):
        payload = {
            "topic": "ATE 测试与可靠性",
            "test_items": ["结构测试（scan/BIST）", "功能测试（指令集一致性）", "时序/电压特性分 bin", "老化与可靠性"],
            "equipment": "ATE（国产优先）/ 实验室自测平台",
            "yield_loop": "良率数据 → 设计/工艺反馈闭环",
        }
        path = self.save_contract(payload, "test")
        return self._mk(action="test", result=payload, contract=path)
