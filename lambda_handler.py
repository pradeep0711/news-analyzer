"""AWS Lambda handler bridging API Gateway events to the Flask app."""

from __future__ import annotations

import logging

import serverless_wsgi

from app import app


LOGGER = logging.getLogger(__name__)


def lambda_handler(event, context):  # pragma: no cover - executed in Lambda
    LOGGER.info("Received event: %s", event.get("requestContext", {}))
    return serverless_wsgi.handle_request(app, event, context)

