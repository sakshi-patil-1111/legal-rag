"""LLM provider abstraction for query rewriting and HyDE.

Supports Google Gemini (free tier) and any OpenAI-compatible endpoint
(Ollama, Groq, OpenAI, etc.) via a single interface.

Configuration via environment variables in .env:
  LLM_PROVIDER=gemini|openai_compatible
  GEMINI_API_KEY=...
  LLM_BASE_URL=http://localhost:11434/v1  (for Ollama)
  LLM_API_KEY=...                          (for OpenAI-compatible)
  LLM_MODEL=gemini-2.5-flash              (or llama3.2:3b for Ollama)
"""

import json
import os
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    text: str
    latency_seconds: float
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    model: str = ""


class LLMProvider:
    """Minimal LLM provider — no SDK dependencies, just HTTP calls."""

    def __init__(
        self,
        provider: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.provider = provider or os.getenv("LLM_PROVIDER", "gemini")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY", "")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "")
        self.model = model or os.getenv("LLM_MODEL", "gemini-3.6-flash")

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 512,
    ) -> LLMResponse:
        if self.provider == "gemini":
            return self._generate_gemini(prompt, system, temperature, max_tokens)
        else:
            return self._generate_openai_compat(prompt, system, temperature, max_tokens)

    def _generate_gemini(
        self, prompt: str, system: str, temperature: float, max_tokens: int,
    ) -> LLMResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": system}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        start = time.perf_counter()
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"Gemini API error {e.code}: {body}") from e

        latency = time.perf_counter() - start
        text = ""
        tokens_in = 0
        tokens_out = 0
        try:
            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts)
            usage = result.get("usageMetadata", {})
            tokens_in = usage.get("promptTokenCount", 0)
            tokens_out = usage.get("candidatesTokenCount", 0)
        except (KeyError, IndexError):
            pass

        return LLMResponse(
            text=text,
            latency_seconds=latency,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=self.model,
        )

    def _generate_openai_compat(
        self, prompt: str, system: str, temperature: float, max_tokens: int,
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        start = time.perf_counter()
        data = json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            raise RuntimeError(f"LLM API error {e.code}: {body}") from e

        latency = time.perf_counter() - start
        text = ""
        tokens_in = 0
        tokens_out = 0
        try:
            text = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            tokens_in = usage.get("prompt_tokens", 0)
            tokens_out = usage.get("completion_tokens", 0)
        except (KeyError, IndexError):
            pass

        return LLMResponse(
            text=text,
            latency_seconds=latency,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=self.model,
        )
