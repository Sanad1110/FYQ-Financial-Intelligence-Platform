"""
Financial Service

واجهة موحدة لجميع العمليات المالية.
"""

from core.financial_engine import (
    build_income,
    build_balance,
    build_cashflow,
    calculate_ratios,
    FinancialRatios,
)


def income_to_dict(obj):
    return obj.__dict__


def balance_to_dict(obj):
    return obj.__dict__


def cashflow_to_dict(obj):
    return obj.__dict__


class FinancialService:

    @staticmethod
    def income(data):
        return build_income(data)

    @staticmethod
    def balance(data):
        return build_balance(data)

    @staticmethod
    def cashflow(data):
        return build_cashflow(data)

    @staticmethod
    def ratios(income, balance, cashflow=None):
        return calculate_ratios(
            income,
            balance,
            cashflow
        )

    @staticmethod
    def ratio_engine(
        income,
        balance,
        cashflow=None,
        sector=""
    ):
        return FinancialRatios(
            income,
            balance,
            cashflow,
            sector
        )
