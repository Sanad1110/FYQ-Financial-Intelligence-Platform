from flask import Blueprint, request, jsonify

from services.financial_service import (
    FinancialService,
)

from services.valuation_service import (
    ValuationService,
)


valuation_bp = Blueprint(
    "valuation",
    __name__
)


@valuation_bp.route(
    "/api/valuation",
    methods=["POST"]
)
def api_valuation():

    from utils.api import api_error

    try:
        d = request.get_json(
            silent=True
        ) or {}

        inc_d = d.get(
            "income",
            {}
        )

        bal_d = d.get(
            "balance",
            {}
        )

        cf_d = d.get(
            "cashflow"
        ) or {}

        val_d = d.get(
            "valuation"
        ) or {}


        if not inc_d or not bal_d:
            return jsonify({
                "error":
                "يلزم إدخال قائمة الدخل والميزانية"
            }), 400


        income = FinancialService.income(
            inc_d
        )

        balance = FinancialService.balance(
            bal_d
        )

        cashflow = (
            FinancialService.cashflow(cf_d)
            if cf_d
            else None
        )


        result = ValuationService.calculate(
            income,
            balance,
            cashflow,

            wacc=float(
                val_d.get(
                    "wacc",
                    0.08
                )
            ),

            terminal_growth=float(
                val_d.get(
                    "terminal_growth",
                    0.025
                )
            ),

            forecast_years=int(
                val_d.get(
                    "forecast_years",
                    5
                )
            ),

            revenue_growth=float(
                val_d.get(
                    "revenue_growth",
                    0.05
                )
            ),

            pe_multiple=float(
                val_d.get(
                    "pe_multiple",
                    12
                )
            ),

            ps_multiple=float(
                val_d.get(
                    "ps_multiple",
                    2
                )
            ),
        )


        return jsonify({
            "status": "success",
            "valuation": result,
        })


    except Exception as e:
        return api_error(
            "تعذر احتساب التقييم.",
            400,
            e,
        )
