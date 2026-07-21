"""
FYQ - محرك التحليل المالي والمحاسبي
FYQ - Financial Analysis Engine
إطار التحليل المالي المتقدم
"""

from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
#  هياكل البيانات
# ─────────────────────────────────────────────

@dataclass
class IncomeStatement:
    """قائمة الدخل - وفق منهجية التحليل المالي"""
    revenue: float = 0.0                    # الإيرادات
    cost_of_goods_sold: float = 0.0         # تكلفة البضاعة المباعة
    operating_expenses: float = 0.0         # المصاريف التشغيلية
    depreciation: float = 0.0              # الاستهلاك والإطفاء
    interest_expense: float = 0.0          # مصاريف الفائدة
    tax_rate: float = 0.15                  # معدل الضريبة (15% افتراضي)

    @property
    def gross_profit(self) -> float:
        return self.revenue - self.cost_of_goods_sold

    @property
    def ebitda(self) -> float:
        return self.gross_profit - self.operating_expenses

    @property
    def ebit(self) -> float:
        return self.ebitda - self.depreciation

    @property
    def ebt(self) -> float:
        return self.ebit - self.interest_expense

    @property
    def tax(self) -> float:
        return max(0, self.ebt * self.tax_rate)

    @property
    def net_income(self) -> float:
        return self.ebt - self.tax

    @property
    def gross_margin(self) -> float:
        return (self.gross_profit / self.revenue * 100) if self.revenue else 0

    @property
    def net_margin(self) -> float:
        return (self.net_income / self.revenue * 100) if self.revenue else 0

    @property
    def operating_margin(self) -> float:
        return (self.ebit / self.revenue * 100) if self.revenue else 0

    @property
    def ebitda_margin(self) -> float:
        return (self.ebitda / self.revenue * 100) if self.revenue else 0


@dataclass
class BalanceSheet:
    """الميزانية العمومية - وفق منهجية التحليل المالي"""
    # الأصول المتداولة
    cash: float = 0.0                       # النقد وما في حكمه
    accounts_receivable: float = 0.0        # الذمم المدينة
    inventory: float = 0.0                  # المخزون
    other_current_assets: float = 0.0       # أصول متداولة أخرى

    # الأصول الثابتة
    fixed_assets: float = 0.0              # الأصول الثابتة (الإجمالي)
    accumulated_depreciation: float = 0.0  # مجمع الاستهلاك
    other_long_term_assets: float = 0.0    # أصول طويلة الأجل أخرى

    # الالتزامات المتداولة
    accounts_payable: float = 0.0          # الذمم الدائنة
    short_term_debt: float = 0.0           # الديون قصيرة الأجل
    other_current_liabilities: float = 0.0 # التزامات متداولة أخرى

    # الالتزامات طويلة الأجل
    long_term_debt: float = 0.0            # الديون طويلة الأجل
    other_long_term_liabilities: float = 0.0

    # حقوق الملكية
    paid_in_capital: float = 0.0           # رأس المال المدفوع
    retained_earnings: float = 0.0         # الأرباح المحتجزة

    @property
    def current_assets(self) -> float:
        return self.cash + self.accounts_receivable + self.inventory + self.other_current_assets

    @property
    def net_fixed_assets(self) -> float:
        return self.fixed_assets - self.accumulated_depreciation

    @property
    def total_assets(self) -> float:
        return self.current_assets + self.net_fixed_assets + self.other_long_term_assets

    @property
    def current_liabilities(self) -> float:
        return self.accounts_payable + self.short_term_debt + self.other_current_liabilities

    @property
    def total_liabilities(self) -> float:
        return self.current_liabilities + self.long_term_debt + self.other_long_term_liabilities

    @property
    def total_equity(self) -> float:
        return self.paid_in_capital + self.retained_earnings

    @property
    def total_liabilities_equity(self) -> float:
        return self.total_liabilities + self.total_equity

    @property
    def is_balanced(self) -> bool:
        return abs(self.total_assets - self.total_liabilities_equity) < 0.01

    @property
    def working_capital(self) -> float:
        return self.current_assets - self.current_liabilities

    @property
    def net_debt(self) -> float:
        return self.long_term_debt + self.short_term_debt - self.cash

    @property
    def book_value_per_share_base(self) -> float:
        """حقوق الملكية (قاعدة لحساب القيمة الدفترية)"""
        return self.total_equity


@dataclass
class CashFlow:
    """قائمة التدفقات النقدية - الطريقة غير المباشرة"""
    # أنشطة التشغيل
    net_income: float = 0.0
    depreciation_add_back: float = 0.0
    change_in_receivables: float = 0.0      # + تناقص / - تزايد
    change_in_inventory: float = 0.0
    change_in_payables: float = 0.0         # + تزايد / - تناقص
    other_operating: float = 0.0

    # أنشطة الاستثمار
    capex: float = 0.0                      # النفقات الرأسمالية (سالب عادةً)
    asset_sales: float = 0.0
    other_investing: float = 0.0

    # أنشطة التمويل
    debt_issued: float = 0.0
    debt_repaid: float = 0.0               # سالب عادةً
    dividends_paid: float = 0.0            # سالب عادةً
    equity_issued: float = 0.0
    other_financing: float = 0.0

    beginning_cash: float = 0.0

    @property
    def operating_cash_flow(self) -> float:
        return (self.net_income + self.depreciation_add_back +
                self.change_in_receivables + self.change_in_inventory +
                self.change_in_payables + self.other_operating)

    @property
    def investing_cash_flow(self) -> float:
        return self.capex + self.asset_sales + self.other_investing

    @property
    def financing_cash_flow(self) -> float:
        return (self.debt_issued + self.debt_repaid +
                self.dividends_paid + self.equity_issued + self.other_financing)

    @property
    def net_change_in_cash(self) -> float:
        return self.operating_cash_flow + self.investing_cash_flow + self.financing_cash_flow

    @property
    def ending_cash(self) -> float:
        return self.beginning_cash + self.net_change_in_cash

    @property
    def free_cash_flow(self) -> float:
        """التدفق النقدي الحر = التشغيلي + النفقات الرأسمالية"""
        return self.operating_cash_flow + self.capex


# ─────────────────────────────────────────────
#  محرك النسب المالية - منهجيات التحليل المالي المتقدم
# ─────────────────────────────────────────────

class FinancialRatios:
    """حساب جميع النسب المالية وفق إطار التحليل المالي المتقدم"""

    def __init__(self, income: IncomeStatement, balance: BalanceSheet, cashflow: Optional[CashFlow] = None, sector: str = ""):
        self.income = income
        self.balance = balance
        self.cashflow = cashflow
        self.sector = (sector or "").strip()

    # ─── نسب السيولة ───
    def current_ratio(self) -> float:
        """نسبة التداول = الأصول المتداولة / الالتزامات المتداولة"""
        return (self.balance.current_assets / self.balance.current_liabilities
                if self.balance.current_liabilities else 0)

    def quick_ratio(self) -> float:
        """نسبة السيولة السريعة = (الأصول المتداولة - المخزون) / الالتزامات المتداولة"""
        return ((self.balance.current_assets - self.balance.inventory) / self.balance.current_liabilities
                if self.balance.current_liabilities else 0)

    def cash_ratio(self) -> float:
        """نسبة النقد = النقد / الالتزامات المتداولة"""
        return (self.balance.cash / self.balance.current_liabilities
                if self.balance.current_liabilities else 0)

    # ─── نسب الربحية ───
    def return_on_assets(self) -> float:
        """العائد على الأصول ROA = صافي الدخل / إجمالي الأصول"""
        return (self.income.net_income / self.balance.total_assets * 100
                if self.balance.total_assets else 0)

    def return_on_equity(self) -> float:
        """العائد على حقوق الملكية ROE = صافي الدخل / حقوق الملكية"""
        if self.balance.total_equity <= 0:
            return 0
        return self.income.net_income / self.balance.total_equity * 100

    def invested_capital(self) -> float:
        """
        Operating invested capital used consistently by FYQ for ROIC and EVA.
        Definition: book equity + interest-bearing debt - cash and cash equivalents.
        This avoids mixing ROIC and EVA capital bases.
        """
        return (self.balance.total_equity + self.balance.short_term_debt +
                self.balance.long_term_debt - self.balance.cash)

    def return_on_invested_capital(self) -> float:
        """ROIC = NOPAT / invested capital."""
        invested_capital = self.invested_capital()
        return (self.income.ebit * (1 - self.income.tax_rate) / invested_capital * 100
                if invested_capital else 0)

    def return_on_capital_employed(self) -> float:
        """العائد على رأس المال المستخدم ROCE"""
        capital_employed = self.balance.total_assets - self.balance.current_liabilities
        return (self.income.ebit / capital_employed * 100 if capital_employed else 0)

    # ─── نسب الكفاءة ───
    def asset_turnover(self) -> float:
        """معدل دوران الأصول = الإيرادات / إجمالي الأصول"""
        return (self.income.revenue / self.balance.total_assets
                if self.balance.total_assets else 0)

    def inventory_turnover(self) -> float:
        """معدل دوران المخزون = تكلفة البضاعة المباعة / المخزون"""
        return (self.income.cost_of_goods_sold / self.balance.inventory
                if self.balance.inventory else 0)

    def days_inventory(self) -> float:
        """أيام المخزون = 365 / معدل دوران المخزون"""
        it = self.inventory_turnover()
        return (365 / it if it else 0)

    def receivables_turnover(self) -> float:
        """معدل دوران الذمم المدينة = الإيرادات / الذمم المدينة"""
        return (self.income.revenue / self.balance.accounts_receivable
                if self.balance.accounts_receivable else 0)

    def days_receivables(self) -> float:
        """أيام التحصيل = 365 / معدل دوران الذمم"""
        rt = self.receivables_turnover()
        return (365 / rt if rt else 0)

    def payables_turnover(self) -> float:
        """معدل دوران الذمم الدائنة"""
        return (self.income.cost_of_goods_sold / self.balance.accounts_payable
                if self.balance.accounts_payable else 0)

    def days_payables(self) -> float:
        """أيام السداد"""
        pt = self.payables_turnover()
        return (365 / pt if pt else 0)

    def cash_conversion_cycle(self) -> float:
        """دورة تحويل النقد = أيام المخزون + أيام التحصيل - أيام السداد"""
        return self.days_inventory() + self.days_receivables() - self.days_payables()

    # ─── نسب الرفع المالي ───
    def debt_to_equity(self) -> float:
        """إجمالي الدين ذي الفائدة / حقوق الملكية."""
        interest_bearing_debt = self.balance.short_term_debt + self.balance.long_term_debt
        return (interest_bearing_debt / self.balance.total_equity
                if self.balance.total_equity else 0)

    def debt_to_assets(self) -> float:
        """إجمالي الدين ذي الفائدة / إجمالي الأصول."""
        interest_bearing_debt = self.balance.short_term_debt + self.balance.long_term_debt
        return (interest_bearing_debt / self.balance.total_assets
                if self.balance.total_assets else 0)

    def liabilities_to_equity(self) -> float:
        """إجمالي الالتزامات / حقوق الملكية."""
        return (self.balance.total_liabilities / self.balance.total_equity
                if self.balance.total_equity else 0)

    def liabilities_to_assets(self) -> float:
        """إجمالي الالتزامات / إجمالي الأصول."""
        return (self.balance.total_liabilities / self.balance.total_assets
                if self.balance.total_assets else 0)

    def equity_multiplier(self) -> float:
        """مضاعف حقوق الملكية = إجمالي الأصول / حقوق الملكية"""
        return (self.balance.total_assets / self.balance.total_equity
                if self.balance.total_equity else 0)

    def interest_coverage(self) -> float | None:
        """نسبة تغطية الفائدة = EBIT / مصاريف الفائدة"""
        return (self.income.ebit / self.income.interest_expense
                if self.income.interest_expense else None)

    def debt_service_coverage(self) -> float:
        """نسبة تغطية خدمة الدين"""
        if self.cashflow:
            total_debt_service = self.income.interest_expense + abs(self.cashflow.debt_repaid)
            return (self.cashflow.operating_cash_flow / total_debt_service
                    if total_debt_service else 0)
        return 0

    def net_debt_to_ebitda(self) -> float:
        """صافي الدين / EBITDA - مؤشر تحليلي متقدم"""
        ebitda = self.income.ebitda
        net_debt = self.balance.net_debt
        return (net_debt / ebitda) if ebitda > 0 else 0

    # ─── تحليل DuPont الثلاثي والخماسي ───
    def dupont_analysis(self) -> dict:
        """
        تحليل دوبونت المالي
        3 عوامل: ROE = هامش الربح × دوران الأصول × مضاعف الملكية
        5 عوامل: ROE = عبء الضريبة × عبء الفائدة × هامش EBIT × دوران الأصول × مضاعف الملكية
        """
        net_margin = self.income.net_margin / 100
        asset_turn = self.asset_turnover()
        eq_mult    = self.equity_multiplier()

        # ROE الثلاثي
        equity_meaningful = self.balance.total_equity > 0
        roe_3 = net_margin * asset_turn * eq_mult * 100 if equity_meaningful else "N/M"

        # عوامل الخماسي
        tax_burden      = (self.income.net_income / self.income.ebt
                           if self.income.ebt else 0)
        interest_burden = (self.income.ebt / self.income.ebit
                           if self.income.ebit else 0)
        ebit_margin     = self.income.operating_margin / 100
        roe_5           = (tax_burden * interest_burden * ebit_margin * asset_turn * eq_mult * 100
                           if equity_meaningful else "N/M")

        return {
            "ROE الفعلي %":            round(self.return_on_equity(), 2) if equity_meaningful else "N/M",
            "ROE (نموذج 3 عوامل) %":  round(roe_3, 2) if equity_meaningful else "N/M",
            "هامش صافي الدخل %":      round(net_margin * 100, 2),
            "معدل دوران الأصول (x)":  round(asset_turn, 3),
            "مضاعف حقوق الملكية (x)": round(eq_mult, 3),
            "عبء الضريبة":            round(tax_burden, 4),
            "عبء الفائدة":            round(interest_burden, 4),
            "هامش EBIT %":            round(ebit_margin * 100, 2),
            "ROE (نموذج 5 عوامل) %":  round(roe_5, 2) if equity_meaningful else "N/M",
        }

    # ─── القيمة الاقتصادية المضافة EVA ───
    def economic_value_added(self, wacc: float = 0.10) -> dict:
        """
        القيمة الاقتصادية المضافة EVA = NOPAT - (WACC × رأس المال المستثمر)
        NOPAT = EBIT × (1 - معدل الضريبة)
        wacc: تكلفة رأس المال المرجحة (افتراضي 10%)
        """
        nopat = self.income.ebit * (1 - self.income.tax_rate)
        # Same capital base used by ROIC: equity + interest-bearing debt - cash.
        invested_capital = self.invested_capital()
        capital_charge = wacc * invested_capital
        eva = nopat - capital_charge
        eva_spread = (nopat / invested_capital - wacc) * 100 if invested_capital else 0

        return {
            "صافي الربح التشغيلي بعد الضريبة": round(nopat, 2),
            "رأس المال المستثمر": round(invested_capital, 2),
            "أساس رأس المال المستثمر": "حقوق الملكية + الديون ذات الفائدة - النقد",
            f"عبء تكلفة رأس المال عند {wacc*100:.0f}%": round(capital_charge, 2),
            "القيمة الاقتصادية المضافة": round(eva, 2),
            "فارق العائد فوق تكلفة رأس المال %": round(eva_spread, 2),
            "تقييم القيمة الاقتصادية المضافة": ("الشركة تخلق قيمة اقتصادية" if eva > 0
                                                else "الشركة لا تغطي تكلفة رأس المال"),
        }

    # ─── Altman Z-Score: sector-aware private-company model ───
    def altman_z_score(self) -> dict:
        """
        Select the Altman private-company model from the declared sector only:
        - Manufacturing / industrial activity: Altman Z' private manufacturing.
        - Other or unspecified sectors: Altman Z'' private non-manufacturing.
        This is a quantitative distress-screening indicator, not a standalone
        bankruptcy or credit opinion.
        """
        ta = self.balance.total_assets
        tl = self.balance.total_liabilities
        if not ta or not tl:
            return {"خطأ": "لا توجد بيانات كافية لحساب Altman Z-Score"}

        x1 = self.balance.working_capital / ta
        x2 = self.balance.retained_earnings / ta
        x3 = self.income.ebit / ta
        x4 = self.balance.total_equity / tl

        sector_key = self.sector.casefold()
        manufacturing_terms = (
            "manufacturing", "manufacturer", "industrial", "industry",
            "تصنيع", "صناعي", "صناعية", "الصناعة", "الصناعات"
        )
        is_manufacturing = any(term in sector_key for term in manufacturing_terms)

        if is_manufacturing:
            x5 = self.income.revenue / ta
            z = 0.717*x1 + 0.847*x2 + 3.107*x3 + 0.420*x4 + 0.998*x5
            if z > 2.90:
                zone = "المنطقة الآمنة"; risk = "مؤشر تعثر منخفض وفق نموذج Z′"; color_hint = "green"
            elif z >= 1.23:
                zone = "المنطقة الرمادية"; risk = "مؤشر تعثر متوسط وفق نموذج Z′ — يستوجب المراقبة"; color_hint = "orange"
            else:
                zone = "منطقة التعثر"; risk = "مؤشر تعثر مرتفع وفق نموذج Z′ — يستوجب التحليل المتعمق"; color_hint = "red"
            return {
                "Z-Score": round(z, 3),
                "النموذج": "Altman Z′ — الشركات الصناعية الخاصة",
                "المنهجية": "Z′ = 0.717X1 + 0.847X2 + 3.107X3 + 0.420X4 + 0.998X5",
                "حدود التصنيف": "آمن > 2.90 | رمادي 1.23–2.90 | تعثر < 1.23",
                "X1 (رأس المال العامل/الأصول)": round(x1, 4),
                "X2 (الأرباح المحتجزة/الأصول)": round(x2, 4),
                "X3 (EBIT/الأصول)": round(x3, 4),
                "X4 (حقوق الملكية الدفترية/الالتزامات)": round(x4, 4),
                "X5 (المبيعات/الأصول)": round(x5, 4),
                "المنطقة": zone,
                "تقييم المخاطر": risk,
                "ملاحظة منهجية": "مؤشر فحص كمي للتعثر وليس رأيًا ائتمانيًا أو حكمًا مستقلًا على الإفلاس.",
                "_model_code": "ALTMAN_Z_PRIME_PRIVATE_MANUFACTURING",
                "_color": color_hint,
            }

        z = 6.56*x1 + 3.26*x2 + 6.72*x3 + 1.05*x4
        if z > 2.60:
            zone = "المنطقة الآمنة"; risk = "مؤشر تعثر منخفض وفق نموذج Z″"; color_hint = "green"
        elif z >= 1.10:
            zone = "المنطقة الرمادية"; risk = "مؤشر تعثر متوسط وفق نموذج Z″ — يستوجب المراقبة"; color_hint = "orange"
        else:
            zone = "منطقة التعثر"; risk = "مؤشر تعثر مرتفع وفق نموذج Z″ — يستوجب التحليل المتعمق"; color_hint = "red"

        return {
            "Z-Score": round(z, 3),
            "النموذج": "Altman Z″ — الشركات الخاصة غير الصناعية",
            "المنهجية": "Z″ = 6.56X1 + 3.26X2 + 6.72X3 + 1.05X4",
            "حدود التصنيف": "آمن > 2.60 | رمادي 1.10–2.60 | تعثر < 1.10",
            "X1 (رأس المال العامل/الأصول)": round(x1, 4),
            "X2 (الأرباح المحتجزة/الأصول)": round(x2, 4),
            "X3 (EBIT/الأصول)": round(x3, 4),
            "X4 (حقوق الملكية الدفترية/الالتزامات)": round(x4, 4),
            "المنطقة": zone,
            "تقييم المخاطر": risk,
            "ملاحظة منهجية": "مؤشر فحص كمي للتعثر وليس رأيًا ائتمانيًا أو حكمًا مستقلًا على الإفلاس.",
            "_model_code": "ALTMAN_Z_DOUBLE_PRIME_PRIVATE_NON_MANUFACTURING",
            "_color": color_hint,
        }

    def get_all_ratios(self) -> dict:
        """إرجاع جميع النسب في قاموس منظم"""
        return {
            "نسب السيولة": {
                "نسبة التداول":             round(self.current_ratio(), 2),
                "نسبة السيولة السريعة":     round(self.quick_ratio(), 2),
                "نسبة النقد":               round(self.cash_ratio(), 2),
            },
            "نسب الربحية": {
                "هامش المبيعات الإجمالي %": round(self.income.gross_margin, 2),
                "هامش EBITDA %":            round(self.income.ebitda_margin, 2),
                "هامش التشغيل %":           round(self.income.operating_margin, 2),
                "هامش صافي الدخل %":        round(self.income.net_margin, 2),
                "العائد على الأصول ROA %":  round(self.return_on_assets(), 2),
                "العائد على حقوق الملكية ROE %": (round(self.return_on_equity(), 2) if self.balance.total_equity > 0 else "N/M"),
                "العائد على رأس المال ROIC %": round(self.return_on_invested_capital(), 2),
                "العائد على رأس المال المستخدم ROCE %": round(self.return_on_capital_employed(), 2),
            },
            "نسب الكفاءة": {
                "معدل دوران الأصول":        round(self.asset_turnover(), 2),
                "معدل دوران المخزون":       round(self.inventory_turnover(), 2),
                "أيام المخزون":             round(self.days_inventory(), 1),
                "معدل دوران الذمم المدينة": round(self.receivables_turnover(), 2),
                "أيام التحصيل":             round(self.days_receivables(), 1),
                "أيام السداد":              round(self.days_payables(), 1),
                "دورة تحويل النقد (يوم)":  round(self.cash_conversion_cycle(), 1),
            },
            "نسب الرفع المالي": {
                "نسبة الدين إلى حقوق الملكية": round(self.debt_to_equity(), 2),
                "نسبة الدين إلى الأصول":    round(self.debt_to_assets(), 2),
                "مضاعف حقوق الملكية":       round(self.equity_multiplier(), 2),
                "نسبة تغطية الفائدة":       (round(self.interest_coverage(), 2) if self.interest_coverage() is not None else "N/M"),
                "صافي الدين إلى EBITDA (مرة)": (round(self.net_debt_to_ebitda(), 2) if self.income.ebitda > 0 else "N/M"),
            },
        }

    def get_interpretation(self) -> list:
        """تفسير النتائج وتقديم توصيات"""
        notes = []
        cr  = self.current_ratio()
        qr  = self.quick_ratio()
        roe = self.return_on_equity()
        de  = self.debt_to_equity()
        npm = self.income.net_margin
        ccc = self.cash_conversion_cycle()
        ic  = self.interest_coverage()

        if cr >= 2:
            notes.append(("✅", "السيولة", f"نسبة التداول {cr:.2f} ممتازة — الشركة قادرة على سداد التزاماتها بكفاءة عالية."))
        elif cr >= 1:
            notes.append(("⚠️", "السيولة", f"نسبة التداول {cr:.2f} مقبولة — يُنصح بمراقبة السيولة."))
        else:
            notes.append(("❌", "السيولة", f"نسبة التداول {cr:.2f} منخفضة — خطر عدم القدرة على سداد الالتزامات قصيرة الأجل."))

        if qr >= 1:
            notes.append(("✅", "السيولة السريعة", f"نسبة السيولة السريعة {qr:.2f} جيدة."))
        else:
            notes.append(("⚠️", "السيولة السريعة", f"نسبة السيولة السريعة {qr:.2f} — الشركة تعتمد على المخزون لتغطية الالتزامات."))

        if self.balance.total_equity <= 0:
            notes.append(("❌", "الربحية", "العائد على حقوق الملكية N/M — حقوق الملكية غير موجبة، لذلك لا تُفسر نسبة ROE بالطريقة التقليدية."))
        elif roe >= 15:
            notes.append(("✅", "الربحية", f"العائد على حقوق الملكية {roe:.1f}% ممتاز. الحد المرجعي التحليلي المستخدم: 15% فأعلى."))
        elif roe >= 8:
            notes.append(("⚠️", "الربحية", f"العائد على حقوق الملكية {roe:.1f}% مقبول."))
        else:
            notes.append(("❌", "الربحية", f"العائد على حقوق الملكية {roe:.1f}% منخفض — يحتاج تحسين الكفاءة."))

        if npm >= 10:
            notes.append(("✅", "هامش الربح", f"هامش صافي الدخل {npm:.1f}% جيد."))
        elif npm >= 5:
            notes.append(("⚠️", "هامش الربح", f"هامش صافي الدخل {npm:.1f}% متوسط."))
        elif npm > 0:
            notes.append(("⚠️", "هامش الربح", f"هامش صافي الدخل {npm:.1f}% ضعيف — راجع هيكل التكاليف."))
        else:
            notes.append(("❌", "هامش الربح", f"الشركة تحقق خسارة (هامش {npm:.1f}%)."))

        if de <= 1:
            notes.append(("✅", "الرفع المالي", f"نسبة الدين إلى حقوق الملكية {de:.2f} آمنة."))
        elif de <= 2:
            notes.append(("⚠️", "الرفع المالي", f"نسبة الدين إلى حقوق الملكية {de:.2f} مرتفعة نسبياً — راقب مستوى الديون."))
        else:
            notes.append(("❌", "الرفع المالي", f"نسبة الدين إلى حقوق الملكية {de:.2f} مرتفعة جداً — خطر مالي عالٍ."))

        if ic is None:
            notes.append(("✅", "تغطية الفائدة", "تغطية الفائدة N/M — لا توجد مصاريف فوائد، لذلك لا يوجد عبء فائدة قائم للقياس."))
        elif ic > 3:
            notes.append(("✅", "تغطية الفائدة", f"نسبة تغطية الفائدة {ic:.1f}x ممتازة (معيار ≥ 3x)."))
        elif ic >= 1.5:
            notes.append(("⚠️", "تغطية الفائدة", f"نسبة تغطية الفائدة {ic:.1f}x مقبولة."))
        else:
            notes.append(("❌", "تغطية الفائدة", f"نسبة تغطية الفائدة {ic:.1f}x خطيرة — الشركة قد تعجز عن سداد الفوائد."))

        if ccc > 0:
            notes.append(("ℹ️", "دورة النقد", f"دورة تحويل النقد {ccc:.0f} يوم — كلما قلّت كان أفضل."))
        elif ccc <= 0:
            notes.append(("✅", "دورة النقد", f"دورة تحويل النقد {ccc:.0f} يوم — الشركة تحصل قبل أن تدفع (ممتاز)."))

        return notes


# ─────────────────────────────────────────────
#  تحليل نقطة التعادل
# ─────────────────────────────────────────────

def break_even_analysis(fixed_costs: float, variable_cost_per_unit: float,
                         selling_price_per_unit: float, units_sold: float = 0) -> dict:
    """تحليل نقطة التعادل الشامل"""
    contribution_margin = selling_price_per_unit - variable_cost_per_unit
    contribution_margin_ratio = (contribution_margin / selling_price_per_unit
                                  if selling_price_per_unit else 0)
    break_even_units = (fixed_costs / contribution_margin if contribution_margin else 0)
    break_even_revenue = break_even_units * selling_price_per_unit

    result = {
        "هامش المساهمة للوحدة":    round(contribution_margin, 2),
        "نسبة هامش المساهمة %":    round(contribution_margin_ratio * 100, 2),
        "نقطة التعادل (وحدات)":    round(break_even_units, 0),
        "نقطة التعادل (إيرادات)":  round(break_even_revenue, 2),
    }

    if units_sold > 0:
        actual_revenue = units_sold * selling_price_per_unit
        margin_of_safety_units = units_sold - break_even_units
        margin_of_safety_pct = (margin_of_safety_units / units_sold * 100 if units_sold else 0)
        profit = contribution_margin * units_sold - fixed_costs
        result.update({
            "هامش الأمان (وحدات)": round(margin_of_safety_units, 0),
            "هامش الأمان %":       round(margin_of_safety_pct, 2),
            "الربح المتوقع":       round(profit, 2),
        })

    return result


# ─────────────────────────────────────────────
#  تحليل الموازنة التقديرية
# ─────────────────────────────────────────────

def budget_variance_analysis(items: list) -> list:
    """
    تحليل الانحرافات بين الفعلي والمخطط
    items: قائمة من القواميس {name, actual, budget}
    """
    results = []
    for item in items:
        name = item.get("name", "")
        actual = item.get("actual", 0)
        budget = item.get("budget", 0)
        variance = actual - budget
        variance_pct = (variance / budget * 100) if budget else 0
        favorable = variance >= 0
        results.append({
            "البند":       name,
            "الفعلي":      round(actual, 2),
            "المخطط":      round(budget, 2),
            "الانحراف":    round(variance, 2),
            "الانحراف %":  round(variance_pct, 2),
            "الحالة":      "موافق" if favorable else "غير موافق",
        })
    return results


# ─────────────────────────────────────────────
#  نظام التقييم المالي الشامل — 100 درجة
# ─────────────────────────────────────────────

class FinancialScorecard:
    """
    FYQ Financial Diagnostic Score — مؤشر تشخيص مالي داخلي من 100 نقطة.
    لا يمثل تصنيفًا ائتمانيًا. الإصدار 1.1 يفصل بوضوح بين درجة الأداء
    وسلامة البيانات ويعرض أساس كل محور لتقليل مخاطر التفسير الخاطئ.
    """

    WEIGHTS = {
        "السيولة":            20,
        "الربحية":            25,
        "الكفاءة التشغيلية":  20,
        "المديونية":          20,
        "التدفقات النقدية":   15,
    }

    def __init__(self, income: IncomeStatement, balance: BalanceSheet,
                 cashflow: Optional[CashFlow] = None):
        self.income   = income
        self.balance  = balance
        self.cashflow = cashflow
        self.ratios   = FinancialRatios(income, balance, cashflow)

    def _score_liquidity(self) -> tuple:
        """تقييم السيولة — 20 نقطة"""
        score = 0
        details = []
        cr = self.ratios.current_ratio()
        qr = self.ratios.quick_ratio()
        cash_r = self.ratios.cash_ratio()

        # نسبة التداول (8 نقاط)
        if cr >= 2.5:
            s = 8; note = f"نسبة التداول {cr:.2f}x — ممتاز"
        elif cr >= 2.0:
            s = 7; note = f"نسبة التداول {cr:.2f}x — جيد جداً"
        elif cr >= 1.5:
            s = 5; note = f"نسبة التداول {cr:.2f}x — جيد"
        elif cr >= 1.0:
            s = 3; note = f"نسبة التداول {cr:.2f}x — مقبول"
        else:
            s = 0; note = f"نسبة التداول {cr:.2f}x — خطر"
        score += s; details.append(("نسبة التداول", s, 8, note))

        # السيولة السريعة (7 نقاط)
        if qr >= 1.5:
            s = 7; note = f"السيولة السريعة {qr:.2f}x — ممتاز"
        elif qr >= 1.0:
            s = 5; note = f"السيولة السريعة {qr:.2f}x — جيد"
        elif qr >= 0.7:
            s = 3; note = f"السيولة السريعة {qr:.2f}x — مقبول"
        else:
            s = 0; note = f"السيولة السريعة {qr:.2f}x — ضعيف"
        score += s; details.append(("السيولة السريعة", s, 7, note))

        # نسبة النقد (5 نقاط)
        if cash_r >= 0.5:
            s = 5; note = f"نسبة النقد {cash_r:.2f}x — ممتاز"
        elif cash_r >= 0.2:
            s = 3; note = f"نسبة النقد {cash_r:.2f}x — جيد"
        else:
            s = 1; note = f"نسبة النقد {cash_r:.2f}x — منخفض"
        score += s; details.append(("نسبة النقد", s, 5, note))

        return score, details

    def _score_profitability(self) -> tuple:
        """تقييم الربحية — 25 نقطة"""
        score = 0
        details = []

        # هامش مجمل الربح (5 نقاط)
        gm = self.income.gross_margin
        if gm >= 40:   s = 5; note = f"هامش مجمل الربح {gm:.1f}% — ممتاز"
        elif gm >= 25: s = 4; note = f"هامش مجمل الربح {gm:.1f}% — جيد"
        elif gm >= 15: s = 2; note = f"هامش مجمل الربح {gm:.1f}% — مقبول"
        else:          s = 0; note = f"هامش مجمل الربح {gm:.1f}% — ضعيف"
        score += s; details.append(("هامش مجمل الربح", s, 5, note))

        # هامش صافي الدخل (5 نقاط)
        nm = self.income.net_margin
        if nm >= 15:   s = 5; note = f"هامش صافي الدخل {nm:.1f}% — ممتاز"
        elif nm >= 10: s = 4; note = f"هامش صافي الدخل {nm:.1f}% — جيد"
        elif nm >= 5:  s = 2; note = f"هامش صافي الدخل {nm:.1f}% — مقبول"
        elif nm > 0:   s = 1; note = f"هامش صافي الدخل {nm:.1f}% — ضعيف"
        else:          s = 0; note = f"هامش صافي الدخل {nm:.1f}% — خسارة"
        score += s; details.append(("هامش صافي الدخل", s, 5, note))

        # ROE (7 نقاط)
        roe = self.ratios.return_on_equity()
        if self.balance.total_equity <= 0:
            s = 0; note = "ROE N/M — حقوق الملكية غير موجبة"
        elif roe >= 20:   s = 7; note = f"ROE {roe:.1f}% — ممتاز"
        elif roe >= 15: s = 5; note = f"ROE {roe:.1f}% — جيد جداً"
        elif roe >= 10: s = 3; note = f"ROE {roe:.1f}% — جيد"
        elif roe >= 5:  s = 1; note = f"ROE {roe:.1f}% — مقبول"
        else:           s = 0; note = f"ROE {roe:.1f}% — ضعيف"
        score += s; details.append(("ROE", s, 7, note))

        # ROA (5 نقاط)
        roa = self.ratios.return_on_assets()
        if roa >= 10:  s = 5; note = f"ROA {roa:.1f}% — ممتاز"
        elif roa >= 5: s = 3; note = f"ROA {roa:.1f}% — جيد"
        elif roa >= 2: s = 1; note = f"ROA {roa:.1f}% — مقبول"
        else:          s = 0; note = f"ROA {roa:.1f}% — ضعيف"
        score += s; details.append(("ROA", s, 5, note))

        # EBITDA Margin (3 نقاط)
        em = self.income.ebitda_margin
        if em >= 20:   s = 3; note = f"هامش EBITDA {em:.1f}% — ممتاز"
        elif em >= 10: s = 2; note = f"هامش EBITDA {em:.1f}% — جيد"
        elif em > 0:   s = 1; note = f"هامش EBITDA {em:.1f}% — مقبول"
        else:          s = 0; note = f"هامش EBITDA {em:.1f}% — سلبي"
        score += s; details.append(("هامش EBITDA", s, 3, note))

        return score, details

    def _score_efficiency(self) -> tuple:
        """تقييم الكفاءة التشغيلية — 20 نقطة"""
        score = 0
        details = []

        # دوران الأصول (5 نقاط)
        at = self.ratios.asset_turnover()
        if at >= 1.5:   s = 5; note = f"دوران الأصول {at:.2f}x — ممتاز"
        elif at >= 1.0: s = 4; note = f"دوران الأصول {at:.2f}x — جيد"
        elif at >= 0.5: s = 2; note = f"دوران الأصول {at:.2f}x — مقبول"
        else:           s = 0; note = f"دوران الأصول {at:.2f}x — ضعيف"
        score += s; details.append(("دوران الأصول", s, 5, note))

        # دوران المخزون (5 نقاط)
        it = self.ratios.inventory_turnover()
        if it >= 8:    s = 5; note = f"دوران المخزون {it:.1f}x — ممتاز"
        elif it >= 4:  s = 4; note = f"دوران المخزون {it:.1f}x — جيد"
        elif it >= 2:  s = 2; note = f"دوران المخزون {it:.1f}x — مقبول"
        else:          s = 0; note = f"دوران المخزون {it:.1f}x — بطيء"
        score += s; details.append(("دوران المخزون", s, 5, note))

        # أيام التحصيل (5 نقاط)
        dr = self.ratios.days_receivables()
        if dr <= 30:   s = 5; note = f"أيام التحصيل {dr:.0f} يوم — ممتاز"
        elif dr <= 45: s = 4; note = f"أيام التحصيل {dr:.0f} يوم — جيد"
        elif dr <= 60: s = 2; note = f"أيام التحصيل {dr:.0f} يوم — مقبول"
        else:          s = 0; note = f"أيام التحصيل {dr:.0f} يوم — بطيء"
        score += s; details.append(("أيام التحصيل", s, 5, note))

        # دورة تحويل النقد (5 نقاط)
        ccc = self.ratios.cash_conversion_cycle()
        if ccc <= 30:   s = 5; note = f"دورة النقد {ccc:.0f} يوم — ممتاز"
        elif ccc <= 60: s = 3; note = f"دورة النقد {ccc:.0f} يوم — جيد"
        elif ccc <= 90: s = 1; note = f"دورة النقد {ccc:.0f} يوم — مقبول"
        else:           s = 0; note = f"دورة النقد {ccc:.0f} يوم — بطيء"
        score += s; details.append(("دورة تحويل النقد", s, 5, note))

        return score, details

    def _score_leverage(self) -> tuple:
        """تقييم المديونية — 20 نقطة"""
        score = 0
        details = []

        # نسبة الدين/الأصول (7 نقاط)
        da = self.ratios.debt_to_assets()
        if da <= 0.3:   s = 7; note = f"الدين/الأصول {da:.2f} — ممتاز"
        elif da <= 0.5: s = 5; note = f"الدين/الأصول {da:.2f} — جيد"
        elif da <= 0.7: s = 2; note = f"الدين/الأصول {da:.2f} — مرتفع"
        else:           s = 0; note = f"الدين/الأصول {da:.2f} — خطر"
        score += s; details.append(("الدين/الأصول", s, 7, note))

        # تغطية الفائدة (7 نقاط)
        ic = self.ratios.interest_coverage()
        if ic is None:
            s = 7; note = "تغطية الفائدة N/M — لا توجد مصاريف فوائد"
        elif ic >= 5:
            s = 7; note = f"تغطية الفائدة {ic:.1f}x — ممتاز"
        elif ic >= 3:  s = 5; note = f"تغطية الفائدة {ic:.1f}x — جيد"
        elif ic >= 1.5: s = 2; note = f"تغطية الفائدة {ic:.1f}x — مقبول"
        else:           s = 0; note = f"تغطية الفائدة {ic:.1f}x — خطر"
        score += s; details.append(("تغطية الفائدة", s, 7, note))

        # صافي الدين/EBITDA (6 نقاط)
        nd_ebitda = self.ratios.net_debt_to_ebitda()
        if self.income.ebitda <= 0:
            s = 0; note = "الدين/EBITDA N/M — EBITDA غير موجب"
        elif nd_ebitda <= 1:   s = 6; note = f"الدين/EBITDA {nd_ebitda:.2f}x — ممتاز"
        elif nd_ebitda <= 2: s = 4; note = f"الدين/EBITDA {nd_ebitda:.2f}x — جيد"
        elif nd_ebitda <= 3: s = 2; note = f"الدين/EBITDA {nd_ebitda:.2f}x — مقبول"
        else:                s = 0; note = f"الدين/EBITDA {nd_ebitda:.2f}x — مرتفع"
        score += s; details.append(("صافي الدين/EBITDA", s, 6, note))

        return score, details

    def _score_cashflow(self) -> tuple:
        """تقييم التدفقات النقدية — 15 نقطة"""
        score = 0
        details = []

        if not self.cashflow:
            return 0, [("التدفقات النقدية", 0, 15, "لا توجد بيانات تدفقات نقدية")]

        ocf = self.cashflow.operating_cash_flow
        fcf = self.cashflow.free_cash_flow
        revenue = self.income.revenue

        # التدفق التشغيلي (6 نقاط)
        ocf_margin = (ocf / revenue * 100) if revenue else 0
        if ocf_margin >= 15:   s = 6; note = f"التدفق التشغيلي {ocf_margin:.1f}% من الإيرادات — ممتاز"
        elif ocf_margin >= 8:  s = 4; note = f"التدفق التشغيلي {ocf_margin:.1f}% — جيد"
        elif ocf_margin >= 3:  s = 2; note = f"التدفق التشغيلي {ocf_margin:.1f}% — مقبول"
        elif ocf > 0:          s = 1; note = f"التدفق التشغيلي موجب — ضعيف"
        else:                  s = 0; note = f"التدفق التشغيلي سلبي — خطر"
        score += s; details.append(("التدفق التشغيلي", s, 6, note))

        # FCF (5 نقاط)
        fcf_margin = (fcf / revenue * 100) if revenue else 0
        if fcf_margin >= 10:  s = 5; note = f"FCF {fcf_margin:.1f}% — ممتاز"
        elif fcf_margin >= 5: s = 3; note = f"FCF {fcf_margin:.1f}% — جيد"
        elif fcf > 0:         s = 1; note = f"FCF موجب — مقبول"
        else:                 s = 0; note = f"FCF سلبي — يحتاج مراجعة"
        score += s; details.append(("التدفق النقدي الحر FCF", s, 5, note))

        # جودة الأرباح (4 نقاط) — OCF / Net Income
        ni = self.income.net_income
        quality = (ocf / ni) if ni > 0 else 0
        if ni <= 0:
            s = 0; note = "جودة الأرباح N/M — صافي الدخل غير موجب"
        elif quality >= 1.2:   s = 4; note = f"جودة الأرباح {quality:.2f} — ممتاز (OCF > صافي الدخل)"
        elif quality >= 0.8: s = 3; note = f"جودة الأرباح {quality:.2f} — جيد"
        elif quality >= 0.5: s = 1; note = f"جودة الأرباح {quality:.2f} — مقبول"
        else:                s = 0; note = f"جودة الأرباح {quality:.2f} — ضعيف"
        score += s; details.append(("جودة الأرباح", s, 4, note))

        return score, details

    def calculate(self) -> dict:
        """حساب التقييم الشامل وإرجاع النتائج"""
        liq_score,  liq_details  = self._score_liquidity()
        prof_score, prof_details = self._score_profitability()
        eff_score,  eff_details  = self._score_efficiency()
        lev_score,  lev_details  = self._score_leverage()
        cf_score,   cf_details   = self._score_cashflow()

        total = liq_score + prof_score + eff_score + lev_score + cf_score
        balance_diff = self.balance.total_assets - self.balance.total_liabilities_equity
        tolerance = max(1.0, abs(self.balance.total_assets) * 0.0001)
        provisional = abs(balance_diff) > tolerance

        # Performance bands deliberately avoid credit-rating symbols (A/A+/B).
        # This is a diagnostic performance score, not a credit opinion.
        if provisional:
            grade = "محجوب"; classification = "سلامة البيانات تحتاج مراجعة"
        elif total >= 90:
            grade = "S1"; classification = "أداء مالي قوي جداً"
        elif total >= 80:
            grade = "S2"; classification = "أداء مالي قوي"
        elif total >= 70:
            grade = "S3"; classification = "أداء مالي جيد"
        elif total >= 60:
            grade = "S4"; classification = "أداء مالي مقبول"
        else:
            grade = "S5"; classification = "أداء مالي يحتاج معالجة"

        statement_coverage = 3 if self.cashflow else 2
        confidence = "مرتفع" if (not provisional and statement_coverage == 3) else ("متوسط" if not provisional else "محجوب")
        axes = {
            "السيولة": {"الدرجة": liq_score, "من": 20, "التفاصيل": liq_details},
            "الربحية": {"الدرجة": prof_score, "من": 25, "التفاصيل": prof_details},
            "الكفاءة التشغيلية": {"الدرجة": eff_score, "من": 20, "التفاصيل": eff_details},
            "المديونية": {"الدرجة": lev_score, "من": 20, "التفاصيل": lev_details},
            "التدفقات النقدية": {"الدرجة": cf_score, "من": 15, "التفاصيل": cf_details},
        }
        test_count = sum(len(axis["التفاصيل"]) for axis in axes.values())
        if any(not str(test[0]).strip() for axis in axes.values() for test in axis["التفاصيل"]):
            raise ValueError("FYQ score audit trail contains an unnamed quantitative test")

        return {
            "التقييم_الإجمالي": total,
            "التصنيف": grade,
            "الوصف": classification,
            "حالة_التقييم": "PROVISIONAL" if provisional else "FINAL",
            "فرق_الميزانية": round(balance_diff, 2),
            "اسم_المنهجية": "FYQ Financial Diagnostic Score",
            "نوع_المنهجية": "PROPRIETARY_INTERNAL_DIAGNOSTIC_MODEL",
            "وصف_المنهجية": f"مؤشر تشخيص أداء مالي داخلي قائم على {test_count} اختبارًا كميًا موزعة على خمسة محاور؛ لا يمثل تصنيفًا ائتمانيًا أو رأيًا استثماريًا.",
            "الأوزان": dict(self.WEIGHTS),
            "إصدار_المنهجية": "FYQ-SCORE-1.2",
            "عدد_الاختبارات": test_count,
            "ثقة_القراءة": confidence,
            "تغطية_القوائم": statement_coverage,
            "المحاور": axes,
        }


# ─────────────────────────────────────────────
#  تحليل المخاطر المالية
# ─────────────────────────────────────────────

class RiskAnalysis:
    """تحليل المخاطر المالية الشامل"""

    RISK_LEVELS = {
        "منخفض":  {"color": "green",  "icon": "✅"},
        "متوسط":  {"color": "orange", "icon": "⚠️"},
        "مرتفع":  {"color": "red",    "icon": "❌"},
    }

    def __init__(self, income: IncomeStatement, balance: BalanceSheet,
                 cashflow: Optional[CashFlow] = None, sector: str = ""):
        self.income   = income
        self.balance  = balance
        self.cashflow = cashflow
        self.ratios   = FinancialRatios(income, balance, cashflow, sector)

    def _risk_level(self, score: float) -> str:
        if score <= 33:   return "منخفض"
        elif score <= 66: return "متوسط"
        else:             return "مرتفع"

    def liquidity_risk(self) -> dict:
        cr = self.ratios.current_ratio()
        qr = self.ratios.quick_ratio()
        if cr >= 2 and qr >= 1:
            level = "منخفض"; score = 15
            desc = "السيولة كافية لتغطية الالتزامات قصيرة الأجل بكفاءة."
        elif cr >= 1.2 or qr >= 0.7:
            level = "متوسط"; score = 50
            desc = f"السيولة مقبولة (التداول: {cr:.2f}x) — يُنصح بمراقبة رأس المال العامل."
        else:
            level = "مرتفع"; score = 85
            desc = f"سيولة منخفضة (التداول: {cr:.2f}x) — خطر عدم القدرة على سداد الالتزامات."
        return {"المخاطرة": "مخاطر السيولة", "المستوى": level,
                "الدرجة": score, "الوصف": desc,
                "icon": self.RISK_LEVELS[level]["icon"]}

    def leverage_risk(self) -> dict:
        da = self.ratios.debt_to_assets()
        ic = self.ratios.interest_coverage()
        if da <= 0.4 and (ic == float('inf') or ic >= 4):
            level = "منخفض"; score = 10
            desc = f"مستوى المديونية آمن. نسبة الدين إلى الأصول {da:.2f}."
        elif da <= 0.6 and (ic == float('inf') or ic >= 2):
            level = "متوسط"; score = 45
            desc = f"مديونية متوسطة. نسبة الدين إلى الأصول {da:.2f} — راقب تغطية الفائدة."
        else:
            level = "مرتفع"; score = 80
            desc = f"مديونية مرتفعة. نسبة الدين إلى الأصول {da:.2f} — خطر مالي عالٍ."
        return {"المخاطرة": "مخاطر المديونية", "المستوى": level,
                "الدرجة": score, "الوصف": desc,
                "icon": self.RISK_LEVELS[level]["icon"]}

    def collection_risk(self) -> dict:
        dr = self.ratios.days_receivables()
        ar = self.balance.accounts_receivable
        rev = self.income.revenue
        ar_pct = (ar / rev * 100) if rev else 0
        if dr <= 45 and ar_pct <= 20:
            level = "منخفض"; score = 15
            desc = f"أيام التحصيل {dr:.0f} يوم — كفاءة تحصيل جيدة."
        elif dr <= 75:
            level = "متوسط"; score = 50
            desc = f"أيام التحصيل {dr:.0f} يوم — يُنصح بتحسين سياسة التحصيل."
        else:
            level = "مرتفع"; score = 80
            desc = f"أيام التحصيل {dr:.0f} يوم — خطر ديون معدومة مرتفع."
        return {"المخاطرة": "مخاطر التحصيل", "المستوى": level,
                "الدرجة": score, "الوصف": desc,
                "icon": self.RISK_LEVELS[level]["icon"]}

    def cashflow_risk(self) -> dict:
        if not self.cashflow:
            return {"المخاطرة": "مخاطر التدفقات النقدية", "المستوى": "متوسط",
                    "الدرجة": 50, "الوصف": "لا توجد بيانات تدفقات نقدية.",
                    "icon": "⚠️"}
        ocf = self.cashflow.operating_cash_flow
        fcf = self.cashflow.free_cash_flow
        if ocf > 0 and fcf > 0:
            level = "منخفض"; score = 10
            desc = f"التدفق التشغيلي {ocf:,.0f} والتدفق الحر {fcf:,.0f} — صحة نقدية ممتازة."
        elif ocf > 0:
            level = "متوسط"; score = 45
            desc = f"التدفق التشغيلي موجب لكن FCF سلبي ({fcf:,.0f}) — راجع النفقات الرأسمالية."
        else:
            level = "مرتفع"; score = 85
            desc = f"التدفق التشغيلي سلبي ({ocf:,.0f}) — خطر نقدي مرتفع."
        return {"المخاطرة": "مخاطر التدفقات النقدية", "المستوى": level,
                "الدرجة": score, "الوصف": desc,
                "icon": self.RISK_LEVELS[level]["icon"]}

    def bankruptcy_risk(self) -> dict:
        z_data = self.ratios.altman_z_score()
        z = z_data.get("Z-Score", 0)
        zone_color = z_data.get("_color")
        if zone_color == "green":
            level = "منخفض"; score = 10
            desc = f"النتيجة الكمية {z:.2f}. تقع ضمن المنطقة الآمنة؛ مؤشر التعثر منخفض."
        elif zone_color == "orange":
            level = "متوسط"; score = 55
            desc = f"النتيجة الكمية {z:.2f}. تقع ضمن المنطقة الرمادية؛ تستوجب المراقبة."
        else:
            level = "مرتفع"; score = 90
            desc = f"النتيجة الكمية {z:.2f}. تقع ضمن منطقة التعثر؛ تستوجب التحليل المتعمق."
        model_symbol = "Z′" if z_data.get("_model_code") == "ALTMAN_Z_PRIME_PRIVATE_MANUFACTURING" else "Z″"
        return {"المخاطرة": f"مؤشر التعثر المالي (Altman {model_symbol})", "المستوى": level,
                "الدرجة": score, "الوصف": desc,
                "icon": self.RISK_LEVELS[level]["icon"]}

    def get_all_risks(self) -> list:
        """إرجاع جميع المخاطر مرتبة حسب الخطورة"""
        risks = [
            self.liquidity_risk(),
            self.leverage_risk(),
            self.collection_risk(),
            self.cashflow_risk(),
            self.bankruptcy_risk(),
        ]
        return sorted(risks, key=lambda r: r["الدرجة"], reverse=True)

    def overall_risk_level(self) -> str:
        risks = self.get_all_risks()
        avg_score = sum(r["الدرجة"] for r in risks) / len(risks)
        if avg_score <= 25:   return "منخفض"
        elif avg_score <= 55: return "متوسط"
        else:                 return "مرتفع"


# ─────────────────────────────────────────────
#  التوصيات الذكية الديناميكية
# ─────────────────────────────────────────────

class SmartRecommendations:
    """توليد توصيات ذكية ديناميكية بناء على نتائج التحليل"""

    def __init__(self, income: IncomeStatement, balance: BalanceSheet,
                 cashflow: Optional[CashFlow] = None):
        self.income   = income
        self.balance  = balance
        self.cashflow = cashflow
        self.ratios   = FinancialRatios(income, balance, cashflow)

    def get_recommendations(self) -> list:
        """
        إرجاع قائمة من التوصيات
        كل توصية: (الأولوية, الفئة, العنوان, التوصية, التأثير_المتوقع)
        الأولوية: 1=عاجل، 2=مهم، 3=تحسين
        """
        recs = []
        cr  = self.ratios.current_ratio()
        qr  = self.ratios.quick_ratio()
        roe = self.ratios.return_on_equity()
        roa = self.ratios.return_on_assets()
        de  = self.ratios.debt_to_equity()
        da  = self.ratios.debt_to_assets()
        ic  = self.ratios.interest_coverage()
        nm  = self.income.net_margin
        gm  = self.income.gross_margin
        dr  = self.ratios.days_receivables()
        di  = self.ratios.days_inventory()
        at  = self.ratios.asset_turnover()
        nd_ebitda = self.ratios.net_debt_to_ebitda()

        # ─── السيولة ───
        if cr < 1.0:
            recs.append((1, "السيولة", "تحسين السيولة عاجل",
                "نسبة التداول أقل من 1 — يُوصى بزيادة الأصول المتداولة عبر تسريع التحصيل أو تقليل المخزون، أو إعادة جدولة الالتزامات قصيرة الأجل إلى طويلة الأجل.",
                "تحسين نسبة التداول بمقدار 0.3-0.5x"))
        elif cr < 1.5:
            recs.append((2, "السيولة", "تعزيز السيولة",
                "يُنصح بمراجعة دورة رأس المال العامل وتقليل أيام التحصيل للحفاظ على سيولة كافية.",
                "تحسين هامش الأمان السيولي"))

        # ─── الربحية ───
        if nm < 0:
            recs.append((1, "الربحية", "معالجة الخسارة فوراً",
                "الشركة تحقق خسارة — يُوصى بمراجعة شاملة لهيكل التكاليف وإلغاء المنتجات/الخدمات غير المربحة، ورفع الأسعار أو تقليل التكاليف الثابتة.",
                "الوصول إلى نقطة التعادل"))
        elif nm < 5:
            recs.append((2, "الربحية", "تحسين هامش الربح",
                f"هامش الربح {nm:.1f}% منخفض — راجع هيكل التسعير وابحث عن فرص خفض التكاليف المتغيرة، وفكر في رفع الأسعار بنسبة 5-10% إذا سمح السوق.",
                f"رفع هامش الربح إلى 8-10%"))

        if gm < 20:
            recs.append((2, "الربحية", "مراجعة هيكل التكاليف",
                f"هامش مجمل الربح {gm:.1f}% منخفض — يُوصى بمراجعة تكاليف الإنتاج والتفاوض مع الموردين للحصول على أسعار أفضل.",
                "رفع هامش مجمل الربح بمقدار 5%"))

        # ─── الكفاءة ───
        if dr > 60:
            recs.append((2, "الكفاءة", "تسريع التحصيل",
                f"أيام التحصيل {dr:.0f} يوم مرتفعة — يُوصى بتطبيق سياسة خصم للدفع المبكر، ومتابعة الذمم المتأخرة بشكل أسبوعي، والنظر في تحديد سقف ائتماني للعملاء.",
                f"تقليل أيام التحصيل إلى 45 يوم"))

        if di > 90:
            recs.append((2, "الكفاءة", "تحسين إدارة المخزون",
                f"أيام المخزون {di:.0f} يوم مرتفعة — يُوصى بتطبيق نظام Just-in-Time أو مراجعة مستويات الطلب لتقليل تكاليف التخزين.",
                "تقليل رأس المال المجمد في المخزون"))

        if at < 0.5:
            recs.append((3, "الكفاءة", "تحسين استخدام الأصول",
                f"معدل دوران الأصول {at:.2f}x منخفض — يُوصى بمراجعة الأصول غير المستخدمة وبيعها أو تأجيرها، وزيادة الإيرادات من الطاقة الإنتاجية الحالية.",
                "رفع معدل دوران الأصول"))

        # ─── المديونية ───
        if da > 0.7:
            recs.append((1, "المديونية", "تقليل الديون عاجل",
                f"نسبة الدين/الأصول {da:.2f} مرتفعة جداً — يُوصى بإعادة هيكلة الديون، وتوقف الاقتراض الجديد، والتركيز على سداد الديون قصيرة الأجل أولاً.",
                "تقليل نسبة الدين/الأصول إلى أقل من 0.5"))
        elif da > 0.5:
            recs.append((2, "المديونية", "مراقبة مستوى الديون",
                f"نسبة الدين/الأصول {da:.2f} — يُنصح بعدم الاقتراض الإضافي والتركيز على سداد الديون الحالية.",
                "الحفاظ على مستوى مديونية مقبول"))

        if ic is not None and ic < 2:
            recs.append((1, "المديونية", "تحسين تغطية الفائدة",
                f"تغطية الفائدة {ic:.1f}x خطيرة — يُوصى بزيادة الأرباح التشغيلية أو إعادة تمويل الديون بأسعار فائدة أقل.",
                "رفع تغطية الفائدة إلى 3x على الأقل"))

        if nd_ebitda > 4:
            recs.append((2, "المديونية", "تخفيض صافي الدين",
                f"صافي الدين/EBITDA = {nd_ebitda:.1f}x مرتفع — الحد المرجعي التحليلي المستخدم ≤ 3x. يُوصى بتخصيص جزء من التدفق النقدي الحر لسداد الديون.",
                "تقليل صافي الدين/EBITDA إلى أقل من 3x"))

        # ─── التدفقات النقدية ───
        if self.cashflow:
            ocf = self.cashflow.operating_cash_flow
            fcf = self.cashflow.free_cash_flow
            if ocf < 0:
                recs.append((1, "التدفقات النقدية", "معالجة التدفق التشغيلي السلبي",
                    f"التدفق التشغيلي سلبي ({ocf:,.0f}) — يُوصى بمراجعة دورة رأس المال العامل وتسريع التحصيل وتأخير المدفوعات.",
                    "تحقيق تدفق تشغيلي موجب"))
            elif fcf < 0 and ocf > 0:
                recs.append((3, "التدفقات النقدية", "مراجعة النفقات الرأسمالية",
                    f"FCF سلبي ({fcf:,.0f}) رغم التدفق التشغيلي الموجب — راجع ما إذا كانت النفقات الرأسمالية ضرورية أو يمكن تأجيلها.",
                    "تحسين التدفق النقدي الحر"))

        # ─── الربحية المتقدمة ───
        if self.balance.total_equity > 0 and roe < 8:
            recs.append((2, "الربحية", "تحسين العائد على الملكية",
                f"ROE = {roe:.1f}% منخفض — يُوصى بزيادة الكفاءة التشغيلية أو إعادة شراء الأسهم لتقليل قاعدة الملكية.",
                f"رفع ROE إلى 15%+"))

        # ─── توصيات تحسين عند عدم وجود تحذيرات ───
        if not recs:
            recs.extend([
                (3, "الاستدامة المالية", "الحفاظ على السيولة",
                 f"نسبة التداول {cr:.2f}x ضمن مستوى مريح؛ يُوصى بالمحافظة على احتياطي سيولة ومراجعة رأس المال العامل دورياً.",
                 "استدامة القدرة على الوفاء بالالتزامات قصيرة الأجل"),
                (3, "الربحية", "إعادة استثمار الفوائض",
                 f"هامش صافي الربح {nm:.1f}% يدعم دراسة إعادة استثمار جزء من الفوائض في المبادرات الأعلى عائداً بعد تقييم المخاطر.",
                 "دعم النمو وتحسين كفاءة تخصيص رأس المال"),
                (3, "الكفاءة", "تحسين دورة التحصيل",
                 f"أيام التحصيل الحالية {dr:.0f} يوم؛ يُوصى بمتابعتها دورياً ووضع هدف تشغيلي لخفضها متى كان ذلك مناسباً لطبيعة النشاط.",
                 "تحسين التدفق النقدي ورأس المال العامل"),
            ])

        # ─── ترتيب حسب الأولوية ───
        recs.sort(key=lambda r: r[0])
        return recs

    def get_executive_summary(self) -> dict:
        """توليد الملخص التنفيذي"""
        scorecard = FinancialScorecard(self.income, self.balance, self.cashflow).calculate()
        risks = RiskAnalysis(self.income, self.balance, self.cashflow).get_all_risks()
        recs = self.get_recommendations()
        ratios = self.ratios

        # نقاط القوة
        strengths = []
        if self.income.gross_margin >= 35:
            strengths.append(f"هامش إجمالي قوي {self.income.gross_margin:.1f}%")
        if ratios.current_ratio() >= 2:
            strengths.append(f"سيولة ممتازة (نسبة التداول {ratios.current_ratio():.2f}x)")
        if self.balance.total_equity > 0 and ratios.return_on_equity() >= 15:
            strengths.append(f"عائد مرتفع على الملكية {ratios.return_on_equity():.1f}%")
        if ratios.interest_coverage() is None:
            strengths.append("لا يوجد عبء فوائد قائم")
        elif ratios.interest_coverage() >= 5:
            strengths.append("تغطية فائدة ممتازة")
        if self.cashflow and self.cashflow.free_cash_flow > 0:
            strengths.append(f"تدفق نقدي حر موجب {self.cashflow.free_cash_flow:,.0f}")
        if ratios.debt_to_assets() < 0.35:
            strengths.append(f"مديونية منخفضة (الدين/الأصول {ratios.debt_to_assets():.2f})")

        # نقاط الضعف
        weaknesses = []
        if self.income.net_margin < 5:
            weaknesses.append(f"هامش صافي منخفض {self.income.net_margin:.1f}%")
        if ratios.current_ratio() < 1.5:
            weaknesses.append(f"سيولة تحتاج تعزيز (التداول {ratios.current_ratio():.2f}x)")
        if ratios.days_receivables() > 60:
            weaknesses.append(f"أيام تحصيل مرتفعة {ratios.days_receivables():.0f} يوم")
        if ratios.debt_to_assets() > 0.6:
            weaknesses.append(f"مديونية مرتفعة (الدين/الأصول {ratios.debt_to_assets():.2f})")
        if ratios.return_on_assets() < 5:
            weaknesses.append(f"ROA منخفض {ratios.return_on_assets():.1f}%")
        if self.cashflow and self.cashflow.operating_cash_flow < 0:
            weaknesses.append("تدفق تشغيلي سلبي")

        # أبرز المخاطر
        top_risks = [r for r in risks if r["المستوى"] in ("مرتفع", "متوسط")][:3]

        # أهم التوصيات
        top_recs = recs[:3]

        return {
            "التقييم_الإجمالي": scorecard["التقييم_الإجمالي"],
            "التصنيف": scorecard["التصنيف"],
            "الوصف": scorecard["الوصف"],
            "نقاط_القوة": strengths[:3],
            "نقاط_الضعف": weaknesses[:3],
            "أبرز_المخاطر": top_risks,
            "أهم_التوصيات": top_recs,
        }


# ─────────────────────────────────────────────
#  المقارنة الزمنية متعددة السنوات
# ─────────────────────────────────────────────

class MultiYearComparison:
    """مقارنة الأداء المالي عبر سنوات متعددة"""

    def __init__(self, years_data: list):
        """
        years_data: قائمة من القواميس
        كل قاموس: {"year": "2023", "income": IncomeStatement, "balance": BalanceSheet, "cashflow": CashFlow}
        """
        self.years_data = sorted(years_data, key=lambda x: x["year"])

    def _growth_rate(self, old: float, new: float) -> float:
        if old and old != 0:
            return (new - old) / abs(old) * 100
        return 0

    def _cagr(self, start: float, end: float, years: int) -> float:
        """معدل النمو السنوي المركب CAGR"""
        if start > 0 and end > 0 and years > 0:
            return ((end / start) ** (1 / years) - 1) * 100
        return 0

    def get_trend_data(self) -> dict:
        """إرجاع بيانات الاتجاه لجميع المؤشرات"""
        if len(self.years_data) < 2:
            return {}

        result = {
            "السنوات": [d["year"] for d in self.years_data],
            "الإيرادات": [],
            "مجمل_الربح": [],
            "EBITDA": [],
            "صافي_الدخل": [],
            "إجمالي_الأصول": [],
            "حقوق_الملكية": [],
            "ROE": [],
            "ROA": [],
            "هامش_الصافي": [],
            "نسبة_التداول": [],
        }

        for d in self.years_data:
            inc = d.get("income")
            bs  = d.get("balance")
            cf  = d.get("cashflow")
            if inc:
                result["الإيرادات"].append(inc.revenue)
                result["مجمل_الربح"].append(inc.gross_profit)
                result["EBITDA"].append(inc.ebitda)
                result["صافي_الدخل"].append(inc.net_income)
                result["هامش_الصافي"].append(inc.net_margin)
            if bs:
                result["إجمالي_الأصول"].append(bs.total_assets)
                result["حقوق_الملكية"].append(bs.total_equity)
            if inc and bs:
                r = FinancialRatios(inc, bs, cf)
                result["ROE"].append(r.return_on_equity())
                result["ROA"].append(r.return_on_assets())
                result["نسبة_التداول"].append(r.current_ratio())

        return result

    def get_growth_analysis(self) -> dict:
        """تحليل نسب النمو بين السنوات"""
        if len(self.years_data) < 2:
            return {}

        growth = {}
        n = len(self.years_data)

        for i in range(1, n):
            prev = self.years_data[i-1]
            curr = self.years_data[i]
            year_label = f"{prev['year']} → {curr['year']}"

            inc_prev = prev.get("income")
            inc_curr = curr.get("income")
            bs_prev  = prev.get("balance")
            bs_curr  = curr.get("balance")

            period_growth = {}
            if inc_prev and inc_curr:
                period_growth["نمو_الإيرادات_%"]    = round(self._growth_rate(inc_prev.revenue, inc_curr.revenue), 2)
                period_growth["نمو_الإجمالي_%"]     = round(self._growth_rate(inc_prev.gross_profit, inc_curr.gross_profit), 2)
                period_growth["نمو_EBITDA_%"]       = round(self._growth_rate(inc_prev.ebitda, inc_curr.ebitda), 2)
                period_growth["نمو_صافي_الدخل_%"]   = round(self._growth_rate(inc_prev.net_income, inc_curr.net_income), 2)
            if bs_prev and bs_curr:
                period_growth["نمو_الأصول_%"]       = round(self._growth_rate(bs_prev.total_assets, bs_curr.total_assets), 2)
                period_growth["نمو_حقوق_الملكية_%"] = round(self._growth_rate(bs_prev.total_equity, bs_curr.total_equity), 2)

            growth[year_label] = period_growth

        # CAGR إذا كانت هناك أكثر من سنتين
        if n >= 3 and self.years_data[0].get("income") and self.years_data[-1].get("income"):
            first_inc = self.years_data[0]["income"]
            last_inc  = self.years_data[-1]["income"]
            years_span = n - 1
            growth["CAGR"] = {
                "CAGR_الإيرادات_%":    round(self._cagr(first_inc.revenue, last_inc.revenue, years_span), 2),
                "CAGR_صافي_الدخل_%":  round(self._cagr(first_inc.net_income, last_inc.net_income, years_span), 2),
            }

        return growth



class BusinessValuation:
    """تقييم قيمة المنشأة باستخدام عدة طرق (DCF, P/E, P/S)"""
    def __init__(self, income: IncomeStatement, balance: BalanceSheet, cashflow: 'CashFlow' = None):
        self.income = income
        self.balance = balance
        self.cashflow = cashflow

    def dcf_valuation(self, wacc: float = 0.08, terminal_growth: float = 0.025, forecast_years: int = 5, revenue_growth: float = 0.05) -> dict:
        """
        حساب قيمة المنشأة بطريقة التدفقات النقدية المخصومة (DCF)
        WACC: معدل الخصم (Weighted Average Cost of Capital)
        terminal_growth: معدل النمو الدائم
        forecast_years: عدد سنوات التنبؤ
        revenue_growth: معدل نمو الإيرادات المتوقع
        """
        if not self.cashflow or self.cashflow.operating_cash_flow <= 0:
            base_fcf = self.income.ebit * (1 - self.income.tax_rate)
        else:
            base_fcf = self.cashflow.operating_cash_flow + self.cashflow.free_cash_flow
            if base_fcf <= 0:
                base_fcf = self.income.net_income

        # توقع التدفقات النقدية الحرة للسنوات القادمة
        fcf_projections = []
        for year in range(1, forecast_years + 1):
            projected_revenue = self.income.revenue * ((1 + revenue_growth) ** year)
            projected_fcf = base_fcf * ((1 + revenue_growth) ** year)
            fcf_projections.append(projected_fcf)

        # حساب القيمة الحالية للتدفقات المتوقعة
        pv_fcf = sum(fcf / ((1 + wacc) ** (i + 1)) for i, fcf in enumerate(fcf_projections))

        # حساب القيمة النهائية (Terminal Value)
        terminal_fcf = fcf_projections[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth) if (wacc - terminal_growth) > 0 else terminal_fcf
        pv_terminal = terminal_value / ((1 + wacc) ** forecast_years)

        # القيمة الإجمالية للمنشأة
        enterprise_value = pv_fcf + pv_terminal
        equity_value = enterprise_value - (self.balance.short_term_debt + self.balance.long_term_debt) + self.balance.cash

        # نطاق التقييم (تحفظ 20% للمخاطر)
        low_value = equity_value * 0.8
        high_value = equity_value * 1.2
        midpoint = (low_value + high_value) / 2

        return {
            'dcf_valuation': equity_value,
            'dcf_low': low_value,
            'dcf_high': high_value,
            'dcf_midpoint': midpoint,
            'pv_fcf': pv_fcf,
            'terminal_value': pv_terminal,
            'enterprise_value': enterprise_value
        }

    def pe_valuation(self, pe_multiple: float = 12) -> float:
        """تقييم بناءً على مضاعف الربح (P/E Valuation)"""
        return self.income.net_income * pe_multiple if self.income.net_income > 0 else 0

    def ps_valuation(self, ps_multiple: float = 2) -> float:
        """تقييم بناءً على مضاعف الإيرادات (P/S Valuation)"""
        return self.income.revenue * ps_multiple if self.income.revenue > 0 else 0

    def calculate_valuation(self, wacc: float = 0.08, terminal_growth: float = 0.025, 
                           forecast_years: int = 5, revenue_growth: float = 0.05,
                           pe_multiple: float = 12, ps_multiple: float = 2) -> dict:
        """حساب التقييم باستخدام جميع الطرق"""
        dcf = self.dcf_valuation(wacc, terminal_growth, forecast_years, revenue_growth)
        pe = self.pe_valuation(pe_multiple)
        ps = self.ps_valuation(ps_multiple)

        # متوسط التقييمات الثلاثة
        valuations = [dcf['dcf_midpoint'], pe, ps]
        valid_valuations = [v for v in valuations if v > 0]
        average = sum(valid_valuations) / len(valid_valuations) if valid_valuations else 0

        return {
            'dcf_valuation': dcf['dcf_midpoint'],
            'dcf_low': dcf['dcf_low'],
            'dcf_high': dcf['dcf_high'],
            'pe_valuation': pe,
            'ps_valuation': ps,
            'average_valuation': average,
            'wacc': wacc,
            'terminal_growth': terminal_growth,
            'forecast_years': forecast_years,
            'revenue_growth': revenue_growth,
            'pe_multiple': pe_multiple,
            'ps_multiple': ps_multiple
        }
