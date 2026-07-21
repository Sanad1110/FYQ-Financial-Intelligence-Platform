from flask import Blueprint, request, jsonify

valuation_bp = Blueprint("valuation", __name__)


@valuation_bp.route('/api/valuation', methods=['POST'])
def api_valuation():
    try:
        from app import build_income, build_balance, build_cashflow, api_error
        from core.financial_engine import BusinessValuation

        d = request.get_json(silent=True) or {}

        inc_d = d.get('income') or {}
        bal_d = d.get('balance') or {}
        cf_d = d.get('cashflow') or {}
        val_d = d.get('valuation') or {}

        if not inc_d or not bal_d:
            return jsonify({
                'error': 'يلزم احتساب قائمة الدخل والميزانية أولاً'
            }), 400

        inc = build_income(inc_d)
        bs = build_balance(bal_d)
        cf = build_cashflow(cf_d) if cf_d else None

        valuation = BusinessValuation(inc, bs, cf)

        result = valuation.calculate_valuation(
            wacc=val_d.get('wacc', 0.08),
            terminal_growth=val_d.get('terminal_growth', 0.025),
            forecast_years=int(val_d.get('forecast_years', 5)),
            revenue_growth=val_d.get('revenue_growth', 0.05),
            pe_multiple=val_d.get('pe_multiple', 12),
            ps_multiple=val_d.get('ps_multiple', 2)
        )

        return jsonify(result)

    except Exception as e:
        return api_error('تعذر احتساب التقييم.',400,e)
