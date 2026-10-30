"""Optional LLM enhancement via a configurable OpenAI-compatible endpoint.

Defaults to a local Ollama server (http://localhost:11434). No API keys are
required. If the endpoint is unreachable, enhancement is skipped gracefully and
the original text is returned unchanged.
"""

import json
import urllib.request
import urllib.error
from typing import Optional

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TIMEOUT = 10


class LLMEnhancer:
    """Rewrite listing text for a target marketplace using a local LLM."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        enabled: bool = True,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.model = model or DEFAULT_MODEL
        self.timeout = timeout
        self.enabled = enabled

    def _chat(self, system: str, user: str) -> Optional[str]:
        if not self.enabled:
            return None
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
        except (urllib.error.URLError, OSError, ValueError):
            return None
        try:
            result = json.loads(body)
        except json.JSONDecodeError:
            return None
        message = result.get("message", {})
        return message.get("content")

    def enhance_for_platform(
        self, platform: str, title: str, description: str, condition_notes: str, pricing_hints: str
    ) -> tuple[str, str]:
        """Return (enhanced_title, enhanced_description). Falls back to originals."""

        system = (
            "You are a careful resale listing assistant. Rewrite the product "
            "title and description for the given marketplace. Keep all facts "
            "from the source record. Do not invent condition, brand, or price "
            "details not present in the source. Be concise, honest, and "
            "beginner-friendly. Return only the rewritten title and description, "
            "labeled 'Title:' and 'Description:'."
        )
        user = (
            f"Marketplace: {platform}\n"
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"Condition notes: {condition_notes}\n"
            f"Pricing hints: {pricing_hints}\n"
        )
        result = self._chat(system, user)
        if not result:
            return title, description
        return self._parse(result, title, description)

    def _parse(self, result: str, fallback_title: str, fallback_description: str) -> tuple[str, str]:
        title = fallback_title
        description = fallback_description
        lower = result.lower()
        if "title:" in lower and "description:" in lower:
            after_title = result.partition("Title:")[2]
            title_part, _, desc_part = after_title.partition("Description:")
            title_candidate = title_part.strip()
            if title_candidate:
                title = title_candidate
            description = desc_part.strip() if desc_part.strip() else fallback_description
        elif "title:" in lower:
            _, _, rest = result.partition("Title:")
            lines = [l for l in rest.splitlines() if l.strip()]
            if lines:
                title = lines[0].strip()
        return title, description
