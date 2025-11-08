"""Utilities for retrieving and extracting article content from the web."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final

import requests
from bs4 import BeautifulSoup
from readability import Document


LOGGER = logging.getLogger(__name__)

DEFAULT_HEADERS: Final[dict[str, str]] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class ArticleRetrievalError(RuntimeError):
    """Raised when article retrieval fails."""


@dataclass(frozen=True)
class ArticleContent:
    """Normalized article details."""

    url: str
    title: str
    text: str


def fetch_article(url: str, timeout: int = 10) -> ArticleContent:
    """Fetch an article and return a cleaned text representation."""

    LOGGER.info("Fetching article %s", url)
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    except requests.RequestException as exc:
        raise ArticleRetrievalError(f"Failed to fetch article: {exc}") from exc

    if response.status_code >= 400:
        raise ArticleRetrievalError(
            f"News site responded with HTTP {response.status_code}: {response.reason}"
        )

    charset = response.encoding or "utf-8"
    html = response.content.decode(charset, errors="ignore")

    document = Document(html)
    title = document.short_title() or "Untitled article"
    summary_html = document.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    if not text:
        raise ArticleRetrievalError("Unable to extract readable text from article content")

    return ArticleContent(url=url, title=title, text=text)

