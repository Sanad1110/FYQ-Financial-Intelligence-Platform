"""
FYQ Financial Intelligence Platform
Main Flask Application
"""

import os
import sys
import uuid
import logging

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, jsonify


# ==========================
# Blueprints
# ==========================

from routes.financial import financial_bp
from routes.engines import engines_bp
from routes.dashboard import dashboard_bp
from routes.scenario import scenario_bp
from routes.benchmark import benchmark_bp
from routes.clients import clients_bp
from routes.projects import projects_bp
from routes.valuation import valuation_bp
from routes.import_export import import_export_bp



# ==========================
# App
# ==========================

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
app.config["JSON_SORT_KEYS"] = False



# ==========================
# Register Routes
# ==========================

app.register_blueprint(financial_bp)
app.register_blueprint(engines_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(scenario_bp)
app.register_blueprint(benchmark_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(valuation_bp)
app.register_blueprint(import_export_bp)



# ==========================
# Logging
# ==========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("FYQ")



# ==========================
# Error Helper
# ==========================

def api_error(message, status=400, exc=None):

    request_id = getattr(
        request,
        "request_id",
        uuid.uuid4().hex[:10]
    )

    if exc:
        logger.exception(
            "request_id=%s | %s",
            request_id,
            exc
        )

    return jsonify({
        "error": message,
        "request_id": request_id
    }), status



# ==========================
# Middleware
# ==========================

@app.before_request
def prepare_request():

    request.request_id = uuid.uuid4().hex[:10]


    if (
        request.path.startswith("/api/")
        and request.method in ["POST","PUT","PATCH"]
    ):

        if (
            request.path != "/api/import/excel"
            and not request.is_json
        ):

            return api_error(
                "JSON body required",
                415
            )



@app.after_request
def security_headers(response):

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Request-ID"] = (
        getattr(request,"request_id","")
    )

    return response



# ==========================
# Error Handling
# ==========================

@app.errorhandler(404)
def not_found(error):

    if request.path.startswith("/api/"):
        return api_error(
            "API route not found",
            404
        )

    return render_template(
        "index.html"
    ),404



@app.errorhandler(413)
def file_large(error):

    return api_error(
        "File too large",
        413
    )



@app.errorhandler(Exception)
def unexpected(error):

    return api_error(
        "Internal server error",
        500,
        error
    )



# ==========================
# Home
# ==========================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )



# ==========================
# Run
# ==========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5050,
        debug=False
    )
