# -*- coding: utf-8 -*-
"""LLM 网关：云端优先，失败自动降级本地 Ollama。无凭据时以规则引擎兜底。"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


class LLMGateway:
    def __init__(self, config_dir: str | Path | None = None, config: dict | None = None):
        self.config = config
        if self.config is None:
            self.config = self._load_config(config_dir)
        self.chain = self.config.get("default_chain", ["cloud", "local"])
        self.cloud_cfg = self.config.get("cloud", {})
        self.local_cfg = self.config.get("local", {})
        self.api_key = os.getenv(self.cloud_cfg.get("api_key_env", "CLOUD_LLM_API_KEY"), "").strip()
        self._stats = {"cloud": 0, "local": 0, "fallback": 0, "errors": 0}

    def _load_config(self, config_dir):
        default = {
            "default_chain": ["cloud", "local"],
            "cloud": {"base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat",
                      "api_key_env": "CLOUD_LLM_API_KEY", "temperature": 0.4, "timeout_seconds": 120},
            "local": {"base_url": "http://127.0.0.1:11434", "model": "qwen2.5:14b",
                      "temperature": 0.4, "timeout_seconds": 300},
        }
        try:
            path = Path(config_dir) / "models.json"
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("加载 models.json 失败: %s", exc)
        return default

    def complete(self, prompt: str, system: str = "", temperature: float | None = None) -> str:
        for provider in self.chain:
            if provider == "cloud" and self.api_key:
                try:
                    text = self._cloud_complete(prompt, system, temperature)
                    self._stats["cloud"] += 1
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("云端 LLM 失败: %s", exc)
                    self._stats["errors"] += 1
            elif provider == "local":
                try:
                    text = self._local_complete(prompt, system, temperature)
                    self._stats["local"] += 1
                    return text
                except Exception as exc:  # noqa: BLE001
                    logger.warning("本地 Ollama 失败: %s", exc)
                    self._stats["errors"] += 1
                    self._stats["fallback"] += 1
        return ""

    def _cloud_complete(self, prompt: str, system: str, temperature: float | None) -> str:
        url = self.cloud_cfg.get("base_url", "").rstrip("/") + "/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.cloud_cfg.get("model", "deepseek-chat"),
            "messages": [{"role": "system", "content": system or "你是芯片设计智能体团队的专业助手。"},
                         {"role": "user", "content": prompt}],
            "temperature": temperature if temperature is not None else self.cloud_cfg.get("temperature", 0.4),
            "max_tokens": 2048,
        }
        resp = requests.post(url, headers=headers, json=payload,
                             timeout=self.cloud_cfg.get("timeout_seconds", 120))
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()

    def _local_complete(self, prompt: str, system: str, temperature: float | None) -> str:
        url = self.local_cfg.get("base_url", "http://127.0.0.1:11434").rstrip("/") + "/api/generate"
        payload = {
            "model": self.local_cfg.get("model", "qwen2.5:14b"),
            "prompt": (system + "\n\n" if system else "") + prompt,
            "stream": False,
            "options": {"temperature": temperature if temperature is not None else self.local_cfg.get("temperature", 0.4)},
        }
        resp = requests.post(url, json=payload, timeout=self.local_cfg.get("timeout_seconds", 300))
        resp.raise_for_status()
        return resp.json().get("response", "").strip()

    def stats(self) -> dict:
        return {"chain": self.chain, "api_key_configured": bool(self.api_key), "stats": self._stats}
