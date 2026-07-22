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
                data.get("cashflow")
            )


        ratios = FinancialRatios(
            inc,
            bs,
            cf,
            data.get("sector", "")
        )


        score = FinancialScorecard(
            ratios
        )


        risk = RiskAnalysis(
            ratios
        )


        return {
            "ratios": ratios.get_all_ratios(),
            "score": score.get_score(),
            "risk": risk.analyze(),
        }
