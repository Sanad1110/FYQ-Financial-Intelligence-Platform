"""
Valuation Service

واجهة موحدة لعمليات التقييم المالي.
"""

from core.financial_engine import BusinessValuation


class ValuationService:

    @staticmethod
    def calculate(
        income,
        balance,
        cashflow=None,
        **kwargs
    ):
        valuation = BusinessValuation(
            income,
            balance,
            cashflow,
        )

        return valuation.calculate_valuation(
            **kwargs
        )
