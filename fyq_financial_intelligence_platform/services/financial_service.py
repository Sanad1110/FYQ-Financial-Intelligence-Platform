import math

from core.financial_engine import (
    IncomeStatement,
    BalanceSheet,
    CashFlow
)


def sf(d, key, default=0.0):
    v = d.get(key, default)

    if v in (None, '', 'null'):
        return default

    try:
        value = float(v)
    except (TypeError, ValueError):
        raise ValueError(f'القيمة في الحقل {key} يجب أن تكون رقمية')

    if not math.isfinite(value):
        raise ValueError(f'القيمة في الحقل {key} غير صالحة')

    if abs(value) > 1_000_000_000_000_000:
        raise ValueError(f'القيمة في الحقل {key} تتجاوز النطاق المسموح')

    return value


def build_income(d):
    tax = sf(d, 'tax_rate', 15)

    if tax > 1:
        tax = tax / 100

    return IncomeStatement(
        revenue=sf(d, 'revenue'),
        cost_of_goods_sold=sf(d, 'cogs') or sf(d, 'cost_of_goods_sold'),
        operating_expenses=sf(d, 'opex') or sf(d, 'operating_expenses'),
        depreciation=sf(d, 'depreciation'),
        interest_expense=sf(d, 'interest') or sf(d, 'interest_expense'),
        tax_rate=tax
    )


def build_balance(d):
    return BalanceSheet(
        cash=sf(d,'cash'),
        accounts_receivable=sf(d,'accounts_receivable'),
        inventory=sf(d,'inventory'),
        other_current_assets=sf(d,'other_current_assets'),
        fixed_assets=sf(d,'fixed_assets'),
        accumulated_depreciation=sf(d,'accumulated_depreciation'),
        other_long_term_assets=sf(d,'other_long_term_assets'),
        accounts_payable=sf(d,'accounts_payable'),
        short_term_debt=sf(d,'short_term_debt'),
        other_current_liabilities=sf(d,'other_current_liabilities'),
        long_term_debt=sf(d,'long_term_debt'),
        other_long_term_liabilities=sf(d,'other_long_term_liabilities'),
        paid_in_capital=sf(d,'paid_in_capital'),
        retained_earnings=sf(d,'retained_earnings')
    )


def income_to_dict(inc):
    return {
        "revenue": inc.revenue,
        "cogs": inc.cost_of_goods_sold,
        "cost_of_goods_sold": inc.cost_of_goods_sold,
        "opex": inc.operating_expenses,
        "operating_expenses": inc.operating_expenses,
        "depreciation": inc.depreciation,
        "interest": inc.interest_expense,
        "interest_expense": inc.interest_expense,
        "tax_rate": inc.tax_rate,
        "gross_profit": inc.gross_profit,
        "ebitda": inc.ebitda,
        "ebit": inc.ebit,
        "net_income": inc.net_income
    }
def balance_to_dict(bs):
    return {
        "cash": bs.cash,
        "accounts_receivable": bs.accounts_receivable,
        "inventory": bs.inventory,
        "other_current_assets": bs.other_current_assets,
        "fixed_assets": bs.fixed_assets,
        "accumulated_depreciation": bs.accumulated_depreciation,
        "other_long_term_assets": bs.other_long_term_assets,
        "accounts_payable": bs.accounts_payable,
        "short_term_debt": bs.short_term_debt,
        "other_current_liabilities": bs.other_current_liabilities,
        "long_term_debt": bs.long_term_debt,
        "other_long_term_liabilities": bs.other_long_term_liabilities,
        "paid_in_capital": bs.paid_in_capital,
        "retained_earnings": bs.retained_earnings,
        "total_current_assets": bs.current_assets,
        "total_non_current_assets": bs.net_fixed_assets + bs.other_long_term_assets,
        "total_assets": bs.total_assets,
        "total_current_liabilities": bs.current_liabilities,
        "total_non_current_liabilities": bs.long_term_debt + bs.other_long_term_liabilities,
        "total_liabilities": bs.total_liabilities,
        "total_equity": bs.total_equity,
        "total_liabilities_equity": bs.total_liabilities_equity,
        "working_capital": bs.working_capital,
        "net_debt": bs.net_debt,
        "is_balanced": bs.is_balanced,
        "balance_diff": round(bs.total_assets - bs.total_liabilities_equity, 2),
    }


def _first_num(d, *keys, default=0.0):
    for key in keys:
        if key in d and d.get(key) not in (None, "", "null"):
            return sf(d, key)
    return default


def _outflow(value):
    value = float(value or 0.0)
    return -abs(value) if value else 0.0


def build_cashflow(d):
    from core.financial_engine import CashFlow

    return CashFlow(
        net_income=sf(d, "net_income"),
        depreciation_add_back=_first_num(
            d,
            "depreciation_add_back",
            "depreciation_cf"
        ),
        change_in_receivables=sf(d, "change_in_receivables"),
        change_in_inventory=sf(d, "change_in_inventory"),
        change_in_payables=sf(d, "change_in_payables"),
        other_operating=sf(d, "other_operating"),
        capex=_outflow(sf(d, "capex")),
        asset_sales=sf(d, "asset_sales"),
        other_investing=sf(d, "other_investing"),
        debt_issued=_first_num(d, "debt_issued", "new_debt"),
        debt_repaid=_outflow(
            _first_num(d, "debt_repaid", "debt_repayment")
        ),
        dividends_paid=_outflow(
            _first_num(d, "dividends_paid", "dividends")
        ),
        equity_issued=_first_num(
            d,
            "equity_issued",
            "stock_issuance"
        ),
        other_financing=sf(d, "other_financing"),
        beginning_cash=sf(d, "beginning_cash"),
    )


def cashflow_to_dict(cf):
    return {
        "net_income": cf.net_income,
        "depreciation_add_back": cf.depreciation_add_back,
        "change_in_receivables": cf.change_in_receivables,
        "change_in_inventory": cf.change_in_inventory,
        "change_in_payables": cf.change_in_payables,
        "other_operating": cf.other_operating,
        "capex": cf.capex,
        "asset_sales": cf.asset_sales,
        "other_investing": cf.other_investing,
        "debt_issued": cf.debt_issued,
        "debt_repaid": cf.debt_repaid,
        "dividends_paid": cf.dividends_paid,
        "equity_issued": cf.equity_issued,
        "other_financing": cf.other_financing,
        "beginning_cash": cf.beginning_cash,
        "operating_cash_flow": cf.operating_cash_flow,
        "investing_cash_flow": cf.investing_cash_flow,
        "financing_cash_flow": cf.financing_cash_flow,
        "net_change_in_cash": cf.net_change_in_cash,
        "ending_cash": cf.ending_cash,
        "free_cash_flow": cf.free_cash_flow,
    }
