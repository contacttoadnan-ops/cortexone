"""
CortexOne LLM Adapter

Supported Providers:
- Ollama (v1)
- OpenAI (planned)
- Claude (planned)
- Gemini (planned)
- MiniMax (planned)
"""

import json
import requests


class LLMAdapter:

    def __init__(
        self,
        provider="ollama",
        model="qwen3:8b",
        host="http://localhost:11434"
    ):

        self.provider = provider.lower()

        self.model = model

        self.host = host.rstrip("/")

    # ---------------------------------------------------
    # Public API
    # ---------------------------------------------------

    def ask(self, prompt: str):

        if self.provider == "ollama":

            return self._ask_ollama(prompt)

        raise ValueError(
            f"Provider '{self.provider}' not supported."
        )

    # ---------------------------------------------------
    # Ollama
    # ---------------------------------------------------

    def _ask_ollama(self, prompt: str):

        url = f"{self.host}/api/generate"

        payload = {

            "model": self.model,

            "prompt": prompt,

            "stream": False

        }

        response = requests.post(
            url,
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        return response.json()["response"]