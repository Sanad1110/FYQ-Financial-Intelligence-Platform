import logging
import secrets

from flask import jsonify


logger = logging.getLogger(__name__)


def api_error(message, status=400, exc=None):
    request_id = secrets.token_hex(5)

    if exc:
        logger.exception(
            "request_id=%s | %s",
            request_id,
            exc,
        )

    return (
        jsonify({
            "error": message,
            "request_id": request_id
        }),
        status,
    )
