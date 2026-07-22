from flask import Blueprint, request, jsonify

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard", methods=["POST"])
def api_dashboard():
    from utils.api import api_error

    try:
        from services.financial_service import (
            build_income,
            build_balance,
            build_cashflow,
        )

        from core.financial_engine import (
            FinancialRatios,
            FinancialScorecard,
            RiskAnalysis,
        )

        d = request.json or {}

        inc = build_income(d.get("income", {}))
        bs = build_balance(d.get("balance", {}))
        cf = (
            build_cashflow(d.get("cashflow", {}))
            if d.get("cashflow")
            else None
        )

        ratios = FinancialRatios(
            inc,
            bs,
            cf,
            d.get("sector", ""),
        )

        score = FinancialScorecard(
            inc,
            bs,
            cf,
        ).calculate()

        risk = RiskAnalysis(
            inc,
            bs,
        )

        dashboard = {
            "score": score,
            "risk": {
                "overall": risk.overall_risk_level(),
                "items": risk.get_all_risks(),
            },
            "balance_status": {
                "is_balanced": bs.is_balanced,
                "difference": round(
                    bs.total_assets - bs.total_liabilities_equity,
                    2,
                ),
            },
        }

        return jsonify(
            {
                "status": "ok",
                "dashboard": dashboard,
            }
        )

    except Exception as e:
        return api_error(
            "تعذر معالجة الطلب. تحقق من صحة البيانات المدخلة.",
            400,
            e,
        )
