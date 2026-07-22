from flask import Blueprint, request, jsonify

from services.financial_service import (
    build_income,
    build_balance,
    build_cashflow,
)

from services.valuation_service import ValuationService

from utils.api import api_error


valuation_bp = Blueprint(
    "valuation",
    __name__
)


@valuation_bp.route(
    "/api/valuation",
    methods=["POST"]
)
def api_valuation():

    try:

        d = request.get_json(
            silent=True
        ) or {}


        inc = build_income(
            d.get("income",{})
        )

        bs = build_balance(
            d.get("balance",{})
        )

        cf = None

        if d.get("cashflow"):
            cf = build_cashflow(
                d.get("cashflow")
            )


        result = ValuationService.calculate(
            inc,
            bs,
            cf,
            **(d.get("valuation") or {})
        )


        return jsonify({
            "status":"success",
            "valuation":result
        })


    except Exception as e:

        return api_error(
            "تعذر احتساب التقييم.",
            400,
            e
        )
