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
