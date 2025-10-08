# agents/llm_provider.py
import os
import json
import requests
from openai import OpenAI
from typing import Optional

class LLMProvider:
    """
    Small LLM provider abstraction. Uses environment variables:
      - LLM_PROVIDER: "openai" (default), "ollama", or "gemini"
      - OPENAI_API_KEY, OPENAI_MODEL
      - OLLAMA_URL, OLLAMA_MODEL
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        # configure openai client if key present
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

    def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
        if self.provider == "openai":
            return self._openai_generate(prompt, temperature, max_tokens)
        if self.provider == "ollama":
            return self._ollama_generate(prompt, temperature, max_tokens)
        if self.provider == "gemini":
            return self._gemini_generate(prompt, temperature, max_tokens)
        raise ValueError(f"Unknown LLM_PROVIDER={self.provider}")

    def _openai_generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not self.openai_client:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        resp = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()

    def _ollama_generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        if "text" in data:
            return data["text"].strip()
        if "choices" in data and len(data["choices"]) > 0:
            ch = data["choices"][0]
            if isinstance(ch, dict) and "content" in ch:
                return ch["content"].strip()
            if isinstance(ch, dict) and "message" in ch and "content" in ch["message"]:
                return ch["message"]["content"].strip()
        return json.dumps(data)[:10000]

    def _gemini_generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        raise NotImplementedError("Gemini provider not implemented in this helper.")
