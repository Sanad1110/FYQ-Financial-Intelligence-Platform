from flask import jsonify


def api_error(message, status=400, exc=None):
    response = {
        "error": message
    }

    return jsonify(response), status
