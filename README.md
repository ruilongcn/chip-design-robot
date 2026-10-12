---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: d32db8dd5a6f99a1df3565db906abe3a_d77767cac07211f18019525400248c00
    ReservedCode1: xGEQI1LRw+oZpxlGyNY2NFZLwV7hdVDR6u6nSEBEn0RCXIgNLNJkuzRVWBugjj7rJiCXR0DNcouSTnQXsVzIUQlwF5Jo14mj9x1FkpKWsPdnQe3rxqYKgsiVkatQiADry7+wDW5d/l64h19mh7BStm0YReyjmNe0L8fVxfw9b55cV0b/dLkgPAz4e1c=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: d32db8dd5a6f99a1df3565db906abe3a_d77767cac07211f18019525400248c00
    ReservedCode2: xGEQI1LRw+oZpxlGyNY2NFZLwV7hdVDR6u6nSEBEn0RCXIgNLNJkuzRVWBugjj7rJiCXR0DNcouSTnQXsVzIUQlwF5Jo14mj9x1FkpKWsPdnQe3rxqYKgsiVkatQiADry7+wDW5d/l64h19mh7BStm0YReyjmNe0L8fVxfw9b55cV0b/dLkgPAz4e1c=
---

# 芯片设计智能体团队（Chip Design Robot Agent Team）

面向自主可控芯片研发的网页版专业智能体团队软件。覆盖芯片架构设计、RTL 设计（Verilog/SystemVerilog）、验证（UVM）、综合/布局布线（EDA）、流片与封装测试、芯片与指令集/BIOS/OS 协同。

> 独立子目录项目：旧工程（backend/frontend）保留在 `F:\chip design robot\` 根目录，本团队项目位于 `chip_design_agent_team\` 子目录。

## 技术栈

- **后端**：FastAPI + Uvicorn（Python 3.11+）
- **多智能体流水线**：Orchestrator 意图解析 → 路由 6 个专业 Agent → JSON 契约落盘（data/）
- **前端**：原生 HTML + CSS + JavaScript（零构建）
- **LLM 网关**：云端优先，失败自动降级本地 Ollama（无 LLM 时规则引擎兜底）

## 智能体团队

| Agent | 职责 |
|---|---|
| chip_architect | 芯片架构设计：微架构、流水线、缓存、互联、PPA 评估 |
| rtl_designer | RTL 设计：Verilog/SystemVerilog 模块、代码生成、Lint |
| verification | 验证：UVM 环境、测试计划、覆盖率、形式验证 |
| eda_flow | 综合/布局布线：逻辑综合、P&R、时序收敛、DFT |
| tapeout_test | 流片与封装测试：流片签核、封装选型、ATE 测试、可靠性 |
| soc_coord | SoC 协同：芯片与指令集/BIOS/OS 协同、启动链路、生态 |

## 快速启动

### 方式一：双击脚本（Windows）

```bat
F:\chip design robot\chip_design_agent_team\scripts\start.bat
```

### 方式二：命令行

```powershell
cd "F:\chip design robot\chip_design_agent_team"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts\start_backend.py
```

启动后浏览器访问：<http://127.0.0.1:8004>

## 目录结构

```
F:\chip design robot\chip_design_agent_team\
├── agents\            # 6 个专业 Agent + orchestrator
├── services\          # llm_gateway
├── web\               # FastAPI 入口 + static 前端
├── scripts\           # 启动脚本
├── config\            # models.json + .env.example
├── data\              # Agent 产出契约
├── requirements.txt
├── README.md
└── 技术方案.md
```

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | / | 前端页面 |
| GET | /api/health | 健康检查 + LLM 状态 |
| GET | /api/agents | Agent 列表 |
| POST | /api/tasks | 提交目标，Orchestrator 规划并执行 |
| GET | /api/tasks/{id} | 查询任务报告 |
| GET | /api/contracts/{sub_dir} | 浏览 data/ 下契约产物 |

详细设计见 [技术方案.md](技术方案.md)。
*（内容由AI生成，仅供参考）*
