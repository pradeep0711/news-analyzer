"""Summarization service built on LangChain and Google Gemini."""

from __future__ import annotations

import logging
import re
from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import Settings


LOGGER = logging.getLogger(__name__)


SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a concise news summarizer. You receive raw article text "
                "along with its source URL. Produce a factual, neutral summary "
                "in under 130 words, using bullet points when it improves clarity. "
                "Include a brief mention of the publication or source if available."
            ),
        ),
        (
            "human",
            (
                "URL: {url}\n\n"
                "Article text:\n{article_text}\n\n"
                "Provide the summary now."
            ),
        ),
    ]
)


class GeminiSummarizer:
    """Encapsulates the LangChain pipeline for Gemini summarization."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._chain = self._build_chain()

    def _build_chain(self) -> RunnableParallel:
        llm = ChatGoogleGenerativeAI(
            model=self._settings.gemini_model,
            temperature=0.2,
            max_output_tokens=512,
        )

        chain = SUMMARY_PROMPT | llm | StrOutputParser()
        return chain

    def summarize(self, *, url: str, article_text: str) -> str:
        LOGGER.info("Invoking Gemini summarizer for %s", url)
        clean_text = _clean_text(article_text, self._settings.max_article_chars)

        response: str = self._chain.invoke({"url": url, "article_text": clean_text})
        return response.strip()


def _clean_text(text: str, max_chars: int) -> str:
    """Normalize whitespace and clip overly long inputs."""

    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) > max_chars:
        LOGGER.warning(
            "Article text truncated from %d to %d characters", len(normalized), max_chars
        )
        return normalized[:max_chars]
    return normalized

