from flask import Blueprint, request, jsonify

financial_bp = Blueprint("financial", __name__)


@financial_bp.route('/api/income', methods=['POST'])
def api_income():
    try:
        from app import build_income, income_to_dict
        d = request.json
        inc = build_income(d)
        return jsonify({'income_statement': income_to_dict(inc)})
    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب. تحقق من صحة البيانات المدخلة.', 400, e)


@financial_bp.route('/api/balance', methods=['POST'])
def api_balance():
    try:
        from app import build_balance, balance_to_dict
        d = request.json
        bs = build_balance(d)
        return jsonify({'balance_sheet': balance_to_dict(bs)})
    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب. تحقق من صحة البيانات المدخلة.', 400, e)


@financial_bp.route('/api/cashflow', methods=['POST'])
def api_cashflow():
    try:
        from app import build_cashflow, cashflow_to_dict
        d = request.json
        cf = build_cashflow(d)
        return jsonify({'cash_flow': cashflow_to_dict(cf)})
    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب. تحقق من صحة البيانات المدخلة.', 400, e)


@financial_bp.route('/api/ratios', methods=['POST'])
def api_ratios():
    try:
        from app import build_income, build_balance, build_cashflow

        from core.financial_engine import FinancialRatios

        d = request.json or {}

        inc_d = d.get('income', {})
        bal_d = d.get('balance', {})
        cf_d = d.get('cashflow') or {}

        inc = build_income(inc_d)
        bs = build_balance(bal_d)
        cf = build_cashflow(cf_d) if cf_d else None

        fr = FinancialRatios(
            inc,
            bs,
            cf,
            d.get('sector', '')
        )

        return jsonify({
            'ratios': {
                'current_ratio': fr.current_ratio(),
                'quick_ratio': fr.quick_ratio(),
                'cash_ratio': fr.cash_ratio(),
                'gross_margin': inc.gross_margin,
                'ebitda_margin': inc.ebitda_margin,
                'operating_margin': inc.operating_margin,
                'net_margin': inc.net_margin,
                'roa': fr.return_on_assets(),
                'roe': fr.return_on_equity(),
                'roic': fr.return_on_invested_capital(),
                'debt_to_assets': fr.debt_to_assets(),
                'debt_to_equity': fr.debt_to_equity(),
                'interest_coverage': fr.interest_coverage(),
                'net_debt_to_ebitda': fr.net_debt_to_ebitda(),
            },
            'ratios_grouped': fr.get_all_ratios(),
            'interpretation': fr.get_interpretation(),
            'dupont': fr.dupont_analysis(),
            'eva': fr.economic_value_added(),
            'altman': fr.altman_z_score(),
        })

    except Exception as e:
        from app import api_error
        return api_error('تعذر معالجة الطلب. تحقق من صحة البيانات المدخلة.', 400, e)
