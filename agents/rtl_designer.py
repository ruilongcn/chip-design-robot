# -*- coding: utf-8 -*-
"""RTL 设计 Agent：Verilog/SystemVerilog 模块设计、代码生成、代码规范检查。"""
from __future__ import annotations

from typing import Any, Dict

from .base_agent import BaseAgent


class RTLDesignerAgent(BaseAgent):
    name = "rtl_designer"
    description = "RTL 设计师：Verilog/SystemVerilog 模块设计、代码生成、Lint 规范检查"

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "module")
        if action == "module":
            return self._module(task)
        if action == "code":
            return self._code(task)
        if action == "lint":
            return self._lint(task)
        return self._module(task)

    def _module(self, task):
        module = task.get("module_name", "cncore_top")
        lang = task.get("lang", "SystemVerilog")
        payload = {
            "module": module,
            "lang": lang,
            "hierarchy": {
                "cncore_top": ["ifu", "idu", "exu", "lsu", "wbu", "csr", "cache_l1", "noc_if"],
                "ifu": ["branch_pred", "btb", "icache_ctrl"],
                "exu": ["alu", "mul", "div", "fpu"],
                "lsu": ["lsq", "dcache_ctrl", "store_buffer"],
            },
            "ports": "标准 AXI4-Lite 控制 + AXI4 数据总线",
            "design_rules": ["同步时序、无锁存器（Latch 0 容忍）", "时钟域同步、跨域用同步器", "参数化模块、可综合 RTL 风格"],
            "next": "由 verification 团队建立 UVM 验证环境",
        }
        path = self.save_contract(payload, "module")
        return self._mk(action="module", result=payload, contract=path)

    def _code(self, task):
        code = """// cncore_alu.sv - 自主核心 ALU（规则模板，正式代码由 Agent 生成）
module cncore_alu #(parameter W = 64)(
    input  logic [W-1:0] a, b,
    input  logic [3:0]   op,
    output logic [W-1:0] y,
    output logic         zero
);
    always_comb begin
        case (op)
            4'h0: y = a & b;
            4'h1: y = a | b;
            4'h2: y = a ^ b;
            4'h3: y = a + b;
            4'h4: y = a - b;
            default: y = {W{1'bx}};
        endcase
    end
    assign zero = (y == {W{1'b0}});
endmodule
"""
        payload = {
            "module": task.get("module_name", "cncore_alu"),
            "lang": task.get("lang", "SystemVerilog"),
            "code_template": code,
            "style": "one-hot 译码、参数化位宽、可综合",
            "note": "正式完整代码建议由本 Agent 依据架构契约生成并做 Lint。",
        }
        path = self.save_contract(payload, "code")
        return self._mk(action="code", result=payload, contract=path)

    def _lint(self, task):
        payload = {
            "topic": "RTL Lint 规范",
            "checks": ["未声明的信号/位宽不匹配", "组合回路/锁存器", "多驱动/竞争", "跨时钟域无同步器", "参数魔数"],
            "tools": "Verilator --lint-only / 自研 lint 规则",
            "severity": {"error": "禁止", "warning": "评审", "info": "建议"},
        }
        path = self.save_contract(payload, "lint")
        return self._mk(action="lint", result=payload, contract=path)
