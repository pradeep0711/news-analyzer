"""Flask application exposing the news summarization endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from flask import Flask, jsonify, request

from src.article_fetcher import ArticleRetrievalError, fetch_article
from src.config import MissingConfigurationError, get_settings
from src.summarizer import GeminiSummarizer


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)

    try:
        settings = get_settings()
    except MissingConfigurationError as exc:
        LOGGER.error("Configuration error: %s", exc)
        raise

    summarizer = GeminiSummarizer(settings)

    @app.route("/summarize", methods=["POST"])
    def summarize() -> Any:
        payload = request.get_json(silent=True) or {}
        url = payload.get("url")

        if not url or not isinstance(url, str):
            return (
                jsonify(
                    {
                        "error": "Invalid request. Provide a JSON body with a non-empty 'url'.",
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            article = fetch_article(url)
            summary = summarizer.summarize(url=url, article_text=article.text)
        except MissingConfigurationError as exc:  # pragma: no cover - defensive
            LOGGER.exception("Configuration error while summarizing")
            return jsonify({"error": str(exc)}), HTTPStatus.INTERNAL_SERVER_ERROR
        except ArticleRetrievalError as exc:
            LOGGER.warning("Article retrieval failed: %s", exc)
            return jsonify({"error": str(exc)}), HTTPStatus.BAD_GATEWAY
        except Exception as exc:  # pragma: no cover - catch-all for runtime issues
            LOGGER.exception("Unexpected error while summarizing")
            return jsonify({"error": "Unexpected error. Please try again later."}), HTTPStatus.INTERNAL_SERVER_ERROR

        return (
            jsonify(
                {
                    "source_url": article.url,
                    "title": article.title,
                    "summary": summary,
                }
            ),
            HTTPStatus.OK,
        )

    @app.route("/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover - local development entrypoint
    app.run(debug=True, host="0.0.0.0", port=8000)

