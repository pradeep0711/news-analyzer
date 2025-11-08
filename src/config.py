"""Configuration utilities for the news summarizer service."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


class MissingConfigurationError(RuntimeError):
    """Raised when a required configuration value is missing."""


@dataclass(frozen=True)
class Settings:
    """Application settings."""

    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    max_article_chars: int = 8000


def get_settings() -> Settings:
    """Load validated settings from the environment."""

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise MissingConfigurationError(
            "GOOGLE_API_KEY is required – set it in your environment or AWS Lambda configuration."
        )

    model_name = os.getenv("GEMINI_MODEL", Settings.gemini_model)

    try:
        max_chars = int(os.getenv("MAX_ARTICLE_CHARS", Settings.max_article_chars))
    except ValueError as exc:
        raise MissingConfigurationError(
            "MAX_ARTICLE_CHARS must be an integer if provided."
        ) from exc

    return Settings(
        google_api_key=api_key,
        gemini_model=model_name,
        max_article_chars=max_chars,
    )

