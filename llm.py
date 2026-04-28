"""LLM クライアント抽象化（Gemini API / Claude Code CLI）

`LLM_BACKEND` 環境変数で生成バックエンドを切り替える:
  - "gemini" (default): 従来どおり google-genai SDK で Gemini API を呼ぶ
  - "claude": ローカルの Claude Code CLI (`claude --print`) を subprocess で呼ぶ
              → Anthropic API 課金不要、Claude Max 枠で動作
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from types import SimpleNamespace

logger = logging.getLogger(__name__)


def _claude_cli_generate(prompt: str, model: str | None = None, timeout: int = 600) -> str:
    """`claude --print` を subprocess で呼んで生成テキストを返す。"""
    claude_model = os.environ.get("CLAUDE_MODEL", model or "claude-haiku-4-5-20251001")
    cmd = [
        os.environ.get("CLAUDE_BIN", "claude"),
        "--print",
        "--output-format", "json",
        "--model", claude_model,
    ]
    logger.debug("Claude CLI 呼び出し: model=%s, prompt_len=%d", claude_model, len(prompt))
    proc = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Claude CLI 失敗 (exit={proc.returncode}): {proc.stderr[:500]}"
        )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Claude CLI 出力 JSON パース失敗: {e}\n生出力: {proc.stdout[:500]}") from e
    if data.get("is_error"):
        raise RuntimeError(f"Claude CLI is_error=true: {data.get('result', '')[:500]}")
    return data.get("result", "")


class _ClaudeModels:
    """google-genai の `client.models` 互換ラッパ"""

    def generate_content(self, model: str, contents, config=None):
        if isinstance(contents, list):
            prompt = "\n".join(str(c) for c in contents)
        else:
            prompt = str(contents)
        text = _claude_cli_generate(prompt, model=None)
        return SimpleNamespace(text=text)


class ClaudeShimClient:
    """`google.genai.Client` 互換最小 shim"""

    def __init__(self, **_kwargs):
        self.models = _ClaudeModels()


def get_llm_client(config) -> object:
    """LLM_BACKEND env と config に基づきクライアントを返す。"""
    backend = os.environ.get("LLM_BACKEND", "gemini").strip().lower()
    if backend == "claude":
        logger.info("LLM backend: Claude Code CLI (Max 枠)")
        return ClaudeShimClient()
    logger.info("LLM backend: Gemini API")
    from google import genai
    if not getattr(config, "GEMINI_API_KEY", None):
        raise ValueError(
            "GEMINI_API_KEY が設定されていません。LLM_BACKEND=claude を指定すれば Gemini 不要です。"
        )
    return genai.Client(api_key=config.GEMINI_API_KEY)
