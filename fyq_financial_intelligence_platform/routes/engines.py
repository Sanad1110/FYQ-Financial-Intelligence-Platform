from flask import Blueprint, request, jsonify

from utils.api import api_error
from services.engines_service import EnginesService

engines_bp = Blueprint("engines", __name__)


@engines_bp.route("/api/engines/budget", methods=["POST"])
def api_budget_engine():
    try:
        return jsonify(
            EnginesService.budget(request.json or {})
        )
    except Exception as e:
        return api_error("تعذر معالجة الطلب.", 400, e)


@engines_bp.route("/api/engines/forecast", methods=["POST"])
def api_forecast_engine():
    try:
        return jsonify(
            EnginesService.forecast(request.json or {})
        )
    except Exception as e:
        return api_error("تعذر معالجة الطلب.", 400, e)


@engines_bp.route("/api/engines/kpi", methods=["POST"])
def api_kpi_engine():
    try:
        return jsonify(
            EnginesService.kpi(request.json or {})
        )
    except Exception as e:
        return api_error("تعذر معالجة الطلب.", 400, e)


@engines_bp.route("/api/engines/variance", methods=["POST"])
def api_variance_engine():
    try:
        return jsonify(
            EnginesService.variance(request.json or {})
        )
    except Exception as e:
        return api_error("تعذر معالجة الطلب.", 400, e)


@engines_bp.route("/api/engines/risk", methods=["POST"])
def api_risk_engine():
    try:
        return jsonify(
            EnginesService.risk(request.json or {})
        )
    except Exception as e:
        return api_error("تعذر معالجة الطلب.", 400, e)


@engines_bp.route("/api/engines/consolidation", methods=["POST"])
def api_consolidation_engine():
    try:
        return jsonify(
            EnginesService.consolidation(request.json or {})
        )
    except Exception as e:
        return api_error("تعذر معالجة الطلب.", 400, e)


@engines_bp.route("/api/engines/dashboard", methods=["POST"])
def api_dashboard_engine():
    try:
        return jsonify(
            EnginesService.dashboard(request.json or {})
        )
    except Exception as e:
        return api_error("تعذر معالجة الطلب.", 400, e)
