"""LLM クライアント抽象化（Gemini API / Claude Code CLI）

`LLM_BACKEND` 環境変数で生成バックエンドを切り替える:
  - "gemini" (default): 従来どおり google-genai SDK で Gemini API を呼ぶ
  - "claude": ローカルの Claude Code CLI (`claude --print`) を subprocess で呼ぶ
              → Anthropic API 課金不要、Claude Max 枠で動作

`get_llm_client(config)` は google-genai 互換の最小 shim を返す。
呼び出し側は `client.models.generate_content(model=..., contents=..., config=...)`
だけを使うため、shim もこのインタフェース1点だけ実装する。
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
from pathlib import Path

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


def _codex_cli_generate(prompt: str, model: str | None = None, timeout: int = 600) -> str:
    """Codex CLI を subprocess で呼んで生成テキストを返す。"""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as pf:
        pf.write(prompt)
        prompt_file = pf.name
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as of:
        output_file = of.name
    try:
        args = os.environ.get(
            "CODEX_ARGS",
            "exec --sandbox read-only --ephemeral --ignore-rules --skip-git-repo-check --output-last-message {output_file} -",
        ).format(prompt_file=prompt_file, output_file=output_file)
        codex_bin = os.environ.get("CODEX_BIN") or shutil.which("codex.cmd") or shutil.which("codex.exe") or shutil.which("codex") or "codex"
        cmd = [codex_bin, *args.split()]
        codex_model = os.environ.get("CODEX_MODEL", "")
        if codex_model:
            cmd.extend(["--model", codex_model])
        logger.debug("Codex CLI 呼び出し: prompt_len=%d", len(prompt))
        proc = subprocess.run(
            cmd,
            input=prompt,
            cwd=tempfile.gettempdir(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        generated = Path(output_file).read_text(encoding="utf-8", errors="replace").strip()
        if proc.returncode != 0 and not generated:
            raise RuntimeError(
                f"Codex CLI 失敗 (exit={proc.returncode}): "
                f"stdout={proc.stdout[-1000:]} stderr={proc.stderr[-2000:]}"
            )
        return generated or proc.stdout
    finally:
        for p in (prompt_file, output_file):
            try:
                Path(p).unlink(missing_ok=True)
            except OSError:
                pass


def _command_generate(prompt: str, timeout: int = 600) -> str:
    """LLM_COMMAND で任意のローカルAIツールを呼ぶ。"""
    template = os.environ.get("LLM_COMMAND", "").strip()
    if not template:
        raise RuntimeError("LLM_COMMAND is required for LLM_BACKEND=command/cursor/grok/openai")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as pf:
        pf.write(prompt)
        prompt_file = pf.name
    output_file = prompt_file + ".out"
    try:
        command = template.format(prompt_file=prompt_file, output_file=output_file)
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"LLM command failed (exit={proc.returncode}): {proc.stderr[:500]}")
        if Path(output_file).exists():
            return Path(output_file).read_text(encoding="utf-8", errors="replace")
        return proc.stdout
    finally:
        for p in (prompt_file, output_file):
            try:
                Path(p).unlink(missing_ok=True)
            except OSError:
                pass


def _provider_generate(prompt: str, model: str | None = None, timeout: int = 600) -> str:
    backend = os.environ.get("LLM_BACKEND", "codex").strip().lower()
    if backend in {"codex", "openai-codex"}:
        return _codex_cli_generate(prompt, model=model, timeout=timeout)
    if backend in {"claude", "claude-code", "anthropic"}:
        return _claude_cli_generate(prompt, model=model, timeout=timeout)
    if backend in {"command", "cursor", "grok", "openai"}:
        return _command_generate(prompt, timeout=timeout)
    raise ValueError(f"Unsupported LLM_BACKEND: {backend}")


class _ClaudeModels:
    """google-genai の `client.models` 互換ラッパ"""

    def generate_content(self, model: str, contents, config=None):
        if isinstance(contents, list):
            prompt = "\n".join(str(c) for c in contents)
        else:
            prompt = str(contents)
        text = _provider_generate(prompt, model=model)
        return SimpleNamespace(text=text)


class ClaudeShimClient:
    """`google.genai.Client` 互換最小 shim"""

    def __init__(self, **_kwargs):
        self.models = _ClaudeModels()


def get_llm_client(config) -> object:
    """設定とenv varからLLMクライアントを返す。

    LLM_BACKEND=codex/claude/command の場合は CLI shim 経由、
    gemini の場合は通常の google-genai Client (config.GEMINI_API_KEY 必須)。
    """
    backend = os.environ.get("LLM_BACKEND", "").strip().lower()
    if not backend:
        backend = "codex"
    if backend in {"codex", "openai-codex", "claude", "claude-code", "anthropic", "command", "cursor", "grok", "openai"}:
        logger.info("LLM backend: %s", backend)
        return ClaudeShimClient()
    logger.info("LLM backend: Gemini API")
    from google import genai
    if not getattr(config, "GEMINI_API_KEY", None):
        raise ValueError(
            "GEMINI_API_KEY が設定されていません。LLM_BACKEND=codex/claude/command を指定すれば Gemini 不要です。"
        )
    return genai.Client(api_key=config.GEMINI_API_KEY)
