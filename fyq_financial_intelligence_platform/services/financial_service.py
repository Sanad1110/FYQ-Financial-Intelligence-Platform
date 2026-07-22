"""
Financial Service

واجهة موحدة لجميع العمليات المالية.
"""

import math

from core.financial_engine import (
    IncomeStatement,
    BalanceSheet,
    CashFlow,
    FinancialRatios,
)


def sf(d, key, default=0.0):

    if not isinstance(d, dict):
        raise ValueError("بنية البيانات غير صحيحة")

    v = d.get(key, default)

    if v in (None, "", "null"):
        return default

    try:
        value = float(v)

    except (TypeError, ValueError):
        raise ValueError(
            f"القيمة في الحقل {key} يجب أن تكون رقمية"
        )

    if not math.isfinite(value):
        raise ValueError(
            f"القيمة في الحقل {key} غير صالحة"
        )

    return value



def build_income(d):

    tax = sf(
        d,
        "tax_rate",
        15
    )

    if tax > 1:
        tax = tax / 100


    return IncomeStatement(
        revenue=sf(d, "revenue"),

        cost_of_goods_sold=
            sf(d, "cogs")
            or sf(d, "cost_of_goods_sold"),

        operating_expenses=
            sf(d, "opex")
            or sf(d, "operating_expenses"),

        depreciation=sf(
            d,
            "depreciation"
        ),

        interest_expense=
            sf(d, "interest")
            or sf(d, "interest_expense"),

        tax_rate=tax
    )



def build_balance(d):

    return BalanceSheet(

        cash=sf(d, "cash"),

        accounts_receivable=
            sf(d, "accounts_receivable"),

        inventory=
            sf(d, "inventory"),

        other_current_assets=
            sf(d, "other_current_assets"),

        fixed_assets=
            sf(d, "fixed_assets"),

        accumulated_depreciation=
            sf(d, "accumulated_depreciation"),

        other_long_term_assets=
            sf(d, "other_long_term_assets"),

        accounts_payable=
            sf(d, "accounts_payable"),

        short_term_debt=
            sf(d, "short_term_debt"),

        other_current_liabilities=
            sf(d, "other_current_liabilities"),

        long_term_debt=
            sf(d, "long_term_debt"),

        other_long_term_liabilities=
            sf(d, "other_long_term_liabilities"),

        paid_in_capital=
            sf(d, "paid_in_capital"),

        retained_earnings=
            sf(d, "retained_earnings")
    )



def _first_num(d, *keys, default=0.0):

    for key in keys:

        if key in d and d.get(key) not in (
            None,
            "",
            "null"
        ):
            return sf(d, key)

    return default



def build_cashflow(d):

    return CashFlow(

        net_income=
            _first_num(
                d,
                "net_income"
            ),

        depreciation_add_back=
            _first_num(
                d,
                "depreciation_add_back",
                "depreciation"
            ),

        change_in_receivables=
            _first_num(
                d,
                "change_in_receivables"
            ),

        change_in_inventory=
            _first_num(
                d,
                "change_in_inventory"
            ),

        change_in_payables=
            _first_num(
                d,
                "change_in_payables"
            ),

        other_operating=
            _first_num(
                d,
                "other_operating"
            ),

        capex=
            _first_num(
                d,
                "capex"
            ),

        asset_sales=
            _first_num(
                d,
                "asset_sales"
            ),

        other_investing=
            _first_num(
                d,
                "other_investing"
            ),

        debt_issued=
            _first_num(
                d,
                "debt_issued"
            ),

        debt_repaid=
            _first_num(
                d,
                "debt_repaid"
            ),

        dividends_paid=
            _first_num(
                d,
                "dividends_paid"
            ),

        equity_issued=
            _first_num(
                d,
                "equity_issued"
            ),

        other_financing=
            _first_num(
                d,
                "other_financing"
            ),

        beginning_cash=
            _first_num(
                d,
                "beginning_cash"
            )
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
    def ratios(
        income,
        balance,
        cashflow
    ):

        return FinancialRatios(
            income,
            balance,
            cashflow
        )
