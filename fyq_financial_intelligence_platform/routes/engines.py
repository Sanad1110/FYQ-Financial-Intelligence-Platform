from flask import Blueprint, request, jsonify

engines_bp = Blueprint("engines", __name__)


@engines_bp.route('/api/engines/budget', methods=['POST'])
def api_budget_engine():
    try:
        from app import api_error
        from core.engines import BudgetEngine

        d = request.json or {}

        result = BudgetEngine(d).run()

        return jsonify(result)

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب.', 400, e)


@engines_bp.route('/api/engines/forecast', methods=['POST'])
def api_forecast_engine():
    try:
        from app import api_error
        from core.engines import ForecastEngine

        d = request.json or {}

        result = ForecastEngine(d).run()

        return jsonify(result)

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب.', 400, e)


@engines_bp.route('/api/engines/kpi', methods=['POST'])
def api_kpi_engine():
    try:
        from app import api_error
        from core.engines import KPIEngine

        d = request.json or {}

        result = KPIEngine(d).run()

        return jsonify(result)

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب.', 400, e)


@engines_bp.route('/api/engines/variance', methods=['POST'])
def api_variance_engine():
    try:
        from app import api_error
        from core.engines import VarianceEngine

        d = request.json or {}

        result = VarianceEngine(d).run()

        return jsonify(result)

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب.', 400, e)


@engines_bp.route('/api/engines/risk', methods=['POST'])
def api_risk_engine():
    try:
        from app import api_error
        from core.engines import RiskEngine

        d = request.json or {}

        result = RiskEngine(d).run()

        return jsonify(result)

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب.', 400, e)


@engines_bp.route('/api/engines/consolidation', methods=['POST'])
def api_consolidation_engine():
    try:
        from app import api_error
        from core.engines import ConsolidationEngine

        d = request.json or {}

        result = ConsolidationEngine(d).run()

        return jsonify(result)

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب.', 400, e)


@engines_bp.route('/api/engines/dashboard', methods=['POST'])
def api_dashboard_engine():
    try:
        from app import api_error
        from core.engines import DashboardEngine

        d = request.json or {}

        result = DashboardEngine(d).run()

        return jsonify(result)

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب.', 400, e)
