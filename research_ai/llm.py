from __future__ import annotations

import logging

from google import genai
from google.genai import types

from .errors import LLMError


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, api_key: str | None, model: str):
        self.model = model
        self.last_status = "not_verified"
        self.status_message = "LLM service not verified."

        if not api_key:
            self._client = None
            self.last_status = "unavailable"
            self.status_message = "GEMINI_API_KEY is not configured."
            return

        try:
            self._client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    timeout=120000,
                    retry_options=types.HttpRetryOptions(
                        attempts=5,
                        initial_delay=1.0,
                        max_delay=20.0,
                    ),
                ),
            )

        except Exception as exc:
            self._client = None
            self.last_status = "unavailable"
            self.status_message = "Gemini client could not be initialized."
            logger.exception("Gemini client initialization failed: %s", exc)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:

        if self._client is None:
            raise LLMError(
                "Gemini is not available. Check GEMINI_API_KEY and the Gemini configuration."
            )

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                ),
            )

            text = (response.text or "").strip()

            if not text:
                raise LLMError(
                    "Gemini returned an empty response."
                )

            self.last_status = "operational"
            self.status_message = "Gemini service operational."

            return text

        except Exception as exc:
            self.last_status = "error"
            self.status_message = "Gemini request failed."

            logger.exception(
                "Gemini request failed for model %s: %s",
                self.model,
                exc,
            )

            raise LLMError(
                "Gemini could not generate a response. "
                "Please try again."
            ) from exc