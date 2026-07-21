from flask import Blueprint, request, jsonify

scenario_bp = Blueprint("scenario", __name__)


@scenario_bp.route('/api/scenario', methods=['POST'])
def api_scenario():
    try:
        from app import scenario_analysis, api_error

        d = request.get_json(silent=True) or {}

        return jsonify(
            scenario_analysis(
                d.get('income') or {},
                d.get('balance') or {},
                d.get('cashflow') or {},
                d.get('changes') or {}
            )
        )

    except Exception as e:
        return api_error('تعذر احتساب السيناريو.', 400, e)
