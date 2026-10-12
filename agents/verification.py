# -*- coding: utf-8 -*-
"""验证 Agent：UVM 验证环境、测试用例规划、覆盖率与形式验证。"""
from __future__ import annotations

from typing import Any, Dict

from .base_agent import BaseAgent


class VerificationAgent(BaseAgent):
    name = "verification"
    description = "验证工程师：UVM 环境、测试计划、覆盖率、形式验证、断言"

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "plan")
        if action == "plan":
            return self._plan(task)
        if action == "uvm":
            return self._uvm(task)
        if action == "cov":
            return self._cov(task)
        return self._plan(task)

    def _plan(self, task):
        payload = {
            "block": task.get("block", "cncore_exu"),
            "test_plan": [
                "算术单元定向用例（加/减/乘/除/移位）",
                "随机指令序列（指令集协同 instruction set 团队）",
                "边界/异常：溢出、除零、非对齐访问",
                "中断/异常注入（协同 openbios/openos）",
                "cache 一致性、多核共享",
                "功耗场景用例",
            ],
            "strategy": "仿真验证为主 + 形式验证（属性检查）+ 覆盖率闭环",
            "metrics": ["行覆盖率 > 90%", "分支覆盖率 > 85%", "状态机覆盖率 100%"],
        }
        path = self.save_contract(payload, "plan")
        return self._mk(action="plan", result=payload, contract=path)

    def _uvm(self, task):
        payload = {
            "topic": "UVM 验证环境",
            "env": {
                "testbench_top": "uvm_testbench 顶层 + 接口绑定",
                "agents": ["stimulus agent（激励）", "monitor agent（监视）", "scoreboard（比对）"],
                "sequence": "base_seq / random_seq / directed_seq",
                "config_db": "接口句柄、覆盖率对象注入",
                "reg_model": "寄存器模型 + 前门/后门访问",
            },
            "simulators": "VCS / Questa / Verilator（开源优先）",
            "note": "验证环境与 RTL 并行开发，回归测试自动化。",
        }
        path = self.save_contract(payload, "uvm")
        return self._mk(action="uvm", result=payload, contract=path)

    def _cov(self, task):
        payload = {
            "topic": "覆盖率与形式验证",
            "functional_cov": ["指令类别交叉覆盖率", "流水线冒险场景", "缓存命中/未命中"],
            "formal": "SVA 断言：总线协议、仲裁公平性、死锁自由",
            "tools": "JasperGold / 开源 SymbiYosys（Yosys-SMT）",
            "close_loop": "覆盖率回灌 → 补充用例 → 回归 → 收敛",
        }
        path = self.save_contract(payload, "cov")
        return self._mk(action="cov", result=payload, contract=path)
