"""
Dashboard Service
"""

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


class DashboardService:

    @staticmethod
    def analyze(data):

        inc = build_income(
            data.get("income", {})
        )

        bs = build_balance(
            data.get("balance", {})
        )

        cf = None

        if data.get("cashflow"):
            cf = build_cashflow(
                data.get("cashflow", {})
            )


        ratios = FinancialRatios(
            inc,
            bs,
            cf,
            data.get("sector", ""),
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


        return {
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
            "ratios": ratios.get_all_ratios(),
        }
