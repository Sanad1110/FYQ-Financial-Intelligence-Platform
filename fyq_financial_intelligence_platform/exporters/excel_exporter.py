"""
FYQ - تصدير تقارير Excel الاحترافية
FYQ - Professional Excel Report Exporter
معايير Advanced Financial Analysis
"""

import os
from datetime import datetime

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ─────────────────────────────────────────────
#  ألوان وأنماط
# ─────────────────────────────────────────────
C = {
    "header":   "0D1117",
    "gold":     "F0C040",
    "accent":   "1F6FEB",
    "success":  "2EA043",
    "danger":   "DA3633",
    "warning":  "D29922",
    "light":    "E6EDF3",
    "dark":     "0D1117",
    "medium":   "161B22",
    "card":     "1C2333",
    "border":   "30363D",
    "purple":   "8957E5",
    "teal":     "39D353",
}

def _fill(hex_color: str) -> "PatternFill":
    return PatternFill("solid", fgColor=hex_color)

def _font(size=11, bold=False, color="E6EDF3", italic=False) -> "Font":
    return Font(name="Calibri", size=size, bold=bold, color=color, italic=italic)

def _align(h="right", v="center", wrap=False) -> "Alignment":
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap, readingOrder=2)

def _border(color="30363D") -> "Border":
    s = Side(style="thin", color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def _cell(ws, row, col, value, font=None, fill=None, align=None, border=None, fmt=None):
    cell = ws.cell(row=row, column=col, value=value)
    if font:   cell.font = font
    if fill:   cell.fill = fill
    if align:  cell.alignment = align
    if border: cell.border = border
    if fmt:    cell.number_format = fmt
    return cell

def _section_header(ws, row, col_start, col_end, text, color=None):
    ws.merge_cells(start_row=row, start_column=col_start,
                   end_row=row, end_column=col_end)
    cell = ws.cell(row=row, column=col_start, value=text)
    cell.font      = _font(size=12, bold=True, color=color or C["gold"])
    cell.fill      = _fill(C["header"])
    cell.alignment = _align("center")
    cell.border    = _border()
    ws.row_dimensions[row].height = 22
    return cell


# ─────────────────────────────────────────────
#  نموذج الاستيراد
# ─────────────────────────────────────────────

def create_template() -> str:
    """إنشاء نموذج Excel للاستيراد"""
    if not HAS_OPENPYXL:
        raise ImportError("يرجى تثبيت openpyxl: pip install openpyxl")

    wb = openpyxl.Workbook()

    # ─── Income ───
    ws = wb.active
    ws.title = "Income"
    ws.sheet_view.rightToLeft = True
    ws.merge_cells("A1:C1")
    _cell(ws, 1, 1, "قائمة الدخل — Income Statement",
          font=_font(14, True, C["gold"]), fill=_fill(C["header"]),
          align=_align("center"), border=_border())

    for col, h in enumerate(["field_name", "value", "description"], 1):
        _cell(ws, 2, col, h, font=_font(10, True, C["gold"]),
              fill=_fill(C["card"]), align=_align("center"), border=_border())

    income_rows = [
        ("revenue",            1000000, "الإيرادات"),
        ("cost_of_goods_sold", 600000,  "تكلفة البضاعة المباعة"),
        ("operating_expenses", 150000,  "المصاريف التشغيلية"),
        ("depreciation",       30000,   "الاستهلاك والإطفاء"),
        ("interest_expense",   20000,   "مصاريف الفائدة"),
        ("tax_rate",           15,      "معدل الضريبة % (أدخل 15 للدلالة على 15%)"),
    ]
    for i, (f, v, d) in enumerate(income_rows, 3):
        _cell(ws, i, 1, f, font=_font(10, color=C["light"]),
              fill=_fill(C["medium"]), align=_align(), border=_border())
        _cell(ws, i, 2, v, font=_font(10, True, C["gold"]),
              fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="#,##0.00")
        _cell(ws, i, 3, d, font=_font(9, italic=True, color=C["light"]),
              fill=_fill(C["medium"]), align=_align("right"), border=_border())

    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 45

    # ─── Balance ───
    ws2 = wb.create_sheet("Balance")
    ws2.sheet_view.rightToLeft = True
    ws2.merge_cells("A1:C1")
    _cell(ws2, 1, 1, "الميزانية العمومية — Balance Sheet",
          font=_font(14, True, C["gold"]), fill=_fill(C["header"]),
          align=_align("center"), border=_border())

    for col, h in enumerate(["field_name", "value", "description"], 1):
        _cell(ws2, 2, col, h, font=_font(10, True, C["gold"]),
              fill=_fill(C["card"]), align=_align("center"), border=_border())

    balance_rows = [
        ("cash",                      200000, "النقد وما في حكمه"),
        ("accounts_receivable",       150000, "الذمم المدينة"),
        ("inventory",                 100000, "المخزون"),
        ("other_current_assets",       50000, "أصول متداولة أخرى"),
        ("fixed_assets",              800000, "الأصول الثابتة (الإجمالي)"),
        ("accumulated_depreciation",  200000, "مجمع الاستهلاك"),
        ("other_long_term_assets",     50000, "أصول طويلة الأجل أخرى"),
        ("accounts_payable",           80000, "الذمم الدائنة"),
        ("short_term_debt",            50000, "ديون قصيرة الأجل"),
        ("other_current_liabilities",  30000, "التزامات متداولة أخرى"),
        ("long_term_debt",            300000, "ديون طويلة الأجل"),
        ("other_long_term_liabilities",20000, "التزامات طويلة الأجل أخرى"),
        ("paid_in_capital",           500000, "رأس المال المدفوع"),
        ("retained_earnings",         170000, "الأرباح المحتجزة"),
    ]
    for i, (f, v, d) in enumerate(balance_rows, 3):
        _cell(ws2, i, 1, f, font=_font(10, color=C["light"]),
              fill=_fill(C["medium"]), align=_align(), border=_border())
        _cell(ws2, i, 2, v, font=_font(10, True, C["gold"]),
              fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="#,##0.00")
        _cell(ws2, i, 3, d, font=_font(9, italic=True, color=C["light"]),
              fill=_fill(C["medium"]), align=_align("right"), border=_border())

    ws2.column_dimensions["A"].width = 32
    ws2.column_dimensions["B"].width = 16
    ws2.column_dimensions["C"].width = 40

    # ─── CashFlow ───
    ws3 = wb.create_sheet("CashFlow")
    ws3.sheet_view.rightToLeft = True
    ws3.merge_cells("A1:C1")
    _cell(ws3, 1, 1, "التدفقات النقدية — Cash Flow Statement",
          font=_font(14, True, C["gold"]), fill=_fill(C["header"]),
          align=_align("center"), border=_border())

    for col, h in enumerate(["field_name", "value", "description"], 1):
        _cell(ws3, 2, col, h, font=_font(10, True, C["gold"]),
              fill=_fill(C["card"]), align=_align("center"), border=_border())

    cf_rows = [
        ("net_income",            170000,  "صافي الدخل"),
        ("depreciation_add_back",  30000,  "الاستهلاك المضاف"),
        ("change_in_receivables", -20000,  "التغير في الذمم المدينة (- تزايد)"),
        ("change_in_inventory",   -10000,  "التغير في المخزون (- تزايد)"),
        ("change_in_payables",     15000,  "التغير في الذمم الدائنة (+ تزايد)"),
        ("other_operating",         5000,  "تعديلات تشغيلية أخرى"),
        ("capex",                 -50000,  "النفقات الرأسمالية CAPEX (سالب)"),
        ("asset_sales",            10000,  "عائدات بيع أصول"),
        ("other_investing",             0, "استثمارات أخرى"),
        ("debt_issued",                 0, "اقتراض جديد"),
        ("debt_repaid",           -30000,  "سداد ديون (سالب)"),
        ("dividends_paid",        -20000,  "توزيعات أرباح (سالب)"),
        ("equity_issued",               0, "إصدار أسهم"),
        ("beginning_cash",        100000,  "رصيد النقد أول الفترة"),
    ]
    for i, (f, v, d) in enumerate(cf_rows, 3):
        _cell(ws3, i, 1, f, font=_font(10, color=C["light"]),
              fill=_fill(C["medium"]), align=_align(), border=_border())
        _cell(ws3, i, 2, v, font=_font(10, True, C["gold"]),
              fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="#,##0.00")
        _cell(ws3, i, 3, d, font=_font(9, italic=True, color=C["light"]),
              fill=_fill(C["medium"]), align=_align("right"), border=_border())

    ws3.column_dimensions["A"].width = 28
    ws3.column_dimensions["B"].width = 16
    ws3.column_dimensions["C"].width = 45

    # ─── تعليمات ───
    ws4 = wb.create_sheet("تعليمات")
    ws4.sheet_view.rightToLeft = True
    ws4.merge_cells("A1:B1")
    _cell(ws4, 1, 1, "تعليمات الاستيراد — FYQ",
          font=_font(14, True, C["gold"]), fill=_fill(C["header"]),
          align=_align("center"), border=_border())

    tips = [
        ("الأوراق المطلوبة",    "Income, Balance, CashFlow — يجب أن تكون الأسماء بالإنجليزية"),
        ("التنسيق",             "العمود الأول: اسم الحقل | العمود الثاني: القيمة الرقمية"),
        ("معدل الضريبة",        "أدخل 15 للدلالة على 15% (وليس 0.15)"),
        ("القيم السالبة",       "أدخل القيم السالبة كـ -50000 للنفقات والسداد"),
        ("أسماء الحقول",        "يجب أن تكون بالإنجليزية كما هو مبين في النموذج"),
        ("الصف الأول",          "يُتجاهل (عنوان) | البيانات تبدأ من الصف الثاني"),
    ]
    for i, (k, v) in enumerate(tips, 3):
        _cell(ws4, i, 1, k, font=_font(10, True, C["gold"]),
              fill=_fill(C["card"]), align=_align(), border=_border())
        _cell(ws4, i, 2, v, font=_font(10, color=C["light"]),
              fill=_fill(C["medium"]), align=_align("right", wrap=True), border=_border())
    ws4.column_dimensions["A"].width = 25
    ws4.column_dimensions["B"].width = 65

    path = os.path.join(os.path.expanduser("~"), "ميزان_Pro_نموذج_استيراد.xlsx")
    wb.save(path)
    return path


# ─────────────────────────────────────────────
#  تصدير التقرير الكامل
# ─────────────────────────────────────────────

def export_full_report(app, output_path: str):
    """تصدير تقرير Excel احترافي شامل"""
    if not HAS_OPENPYXL:
        raise ImportError("يرجى تثبيت openpyxl: pip install openpyxl")

    wb = openpyxl.Workbook()
    company  = getattr(app, "company_name", "شركة نموذجية") or "شركة نموذجية"
    year     = getattr(app, "fiscal_year",  str(datetime.now().year)) or str(datetime.now().year)
    currency = getattr(app, "currency",     "ريال") or "ريال"
    now_str  = datetime.now().strftime("%Y-%m-%d")

    # ─── الغلاف ───
    ws_cover = wb.active
    ws_cover.title = "الغلاف"
    ws_cover.sheet_view.rightToLeft = True
    for row in range(1, 25):
        for col in range(1, 7):
            ws_cover.cell(row, col).fill = _fill(C["dark"])
    for col in range(1, 7):
        ws_cover.column_dimensions[get_column_letter(col)].width = 20

    ws_cover.merge_cells("A1:F1")
    _cell(ws_cover, 1, 1, "FYQ",
          font=_font(30, True, C["gold"]), fill=_fill(C["dark"]), align=_align("center"))
    ws_cover.row_dimensions[1].height = 55

    ws_cover.merge_cells("A3:F3")
    _cell(ws_cover, 3, 1, "التقرير المالي الشامل",
          font=_font(18, True, C["light"]), fill=_fill(C["dark"]), align=_align("center"))

    ws_cover.merge_cells("A4:F4")
    _cell(ws_cover, 4, 1, company,
          font=_font(16, True, C["accent"]), fill=_fill(C["dark"]), align=_align("center"))

    ws_cover.merge_cells("A5:F5")
    _cell(ws_cover, 5, 1, f"السنة المالية: {year}",
          font=_font(13, color=C["light"]), fill=_fill(C["dark"]), align=_align("center"))

    ws_cover.merge_cells("A7:F7")
    _cell(ws_cover, 7, 1, "معايير Professional Financial Analysis Framework",
          font=_font(11, italic=True, color=C["warning"]), fill=_fill(C["dark"]), align=_align("center"))

    ws_cover.merge_cells("A8:F8")
    _cell(ws_cover, 8, 1, f"تاريخ الإصدار: {now_str}",
          font=_font(10, color=C["border"]), fill=_fill(C["dark"]), align=_align("center"))

    ws_cover.merge_cells("A10:F10")
    _cell(ws_cover, 10, 1, "FYQ — Integrated Financial & Accounting Tool v2.0",
          font=_font(9, italic=True, color=C["border"]), fill=_fill(C["dark"]), align=_align("center"))

    # ─── قائمة الدخل ───
    if app.income_data:
        inc = app.income_data
        ws = wb.create_sheet("قائمة الدخل")
        ws.sheet_view.rightToLeft = True
        _sheet_header(ws, f"قائمة الدخل — Income Statement", company, year, 2)

        rows = [
            ("الإيرادات",                      inc.revenue,             True,  C["light"]),
            ("(-) تكلفة البضاعة المباعة",      -inc.cost_of_goods_sold, False, C["danger"]),
            ("= مجمل الربح (Gross Profit)",    inc.gross_profit,        True,  C["success"]),
            ("(-) المصاريف التشغيلية",         -inc.operating_expenses, False, C["danger"]),
            ("= EBITDA",                        inc.ebitda,              True,  C["accent"]),
            ("(-) الاستهلاك والإطفاء",         -inc.depreciation,       False, C["warning"]),
            ("= ربح التشغيل EBIT",              inc.ebit,                True,  C["accent"]),
            ("(-) مصاريف الفائدة",             -inc.interest_expense,   False, C["danger"]),
            ("= الربح قبل الضريبة EBT",         inc.ebt,                 True,  C["accent"]),
            ("(-) ضريبة الدخل",                -inc.tax,                False, C["danger"]),
            ("= صافي الدخل (Net Income)",       inc.net_income,          True,  C["gold"]),
        ]

        _table_header(ws, 4, [f"البند", f"القيمة ({currency})", "النسبة من الإيرادات"])
        for i, (label, val, bold, color) in enumerate(rows, 5):
            bg = C["card"] if bold else C["medium"]
            _cell(ws, i, 1, label, font=_font(10, bold, C["light"]),
                  fill=_fill(bg), align=_align(), border=_border())
            _cell(ws, i, 2, val, font=_font(11, bold, color),
                  fill=_fill(bg), align=_align("left"), border=_border(), fmt="#,##0.00")
            pct = (val / inc.revenue) if inc.revenue else 0
            _cell(ws, i, 3, pct, font=_font(10, bold, color),
                  fill=_fill(bg), align=_align("center"), border=_border(), fmt="0.0%")

        # الهوامش
        row = len(rows) + 6
        _section_header(ws, row, 1, 3, "الهوامش المالية")
        margins = [
            ("هامش مجمل الربح %",  inc.gross_margin / 100),
            ("هامش EBITDA %",    inc.ebitda_margin / 100),
            ("هامش التشغيل %",   inc.operating_margin / 100),
            ("هامش صافي الدخل %",    inc.net_margin / 100),
        ]
        for j, (label, val) in enumerate(margins, row + 1):
            color = C["success"] if val >= 0.1 else (C["warning"] if val >= 0 else C["danger"])
            _cell(ws, j, 1, label, font=_font(10, color=C["light"]),
                  fill=_fill(C["medium"]), align=_align(), border=_border())
            _cell(ws, j, 2, val, font=_font(11, True, color),
                  fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="0.00%")

        ws.column_dimensions["A"].width = 38
        ws.column_dimensions["B"].width = 22
        ws.column_dimensions["C"].width = 20

    # ─── الميزانية العمومية ───
    if app.balance_data:
        bs = app.balance_data
        ws = wb.create_sheet("الميزانية العمومية")
        ws.sheet_view.rightToLeft = True
        _sheet_header(ws, "الميزانية العمومية — Balance Sheet", company, year, 2)

        sections = [
            ("الأصول المتداولة", [
                ("النقد وما في حكمه",        bs.cash),
                ("الذمم المدينة",             bs.accounts_receivable),
                ("المخزون",                   bs.inventory),
                ("أصول متداولة أخرى",        bs.other_current_assets),
                ("إجمالي الأصول المتداولة",  bs.current_assets),
            ], C["accent"]),
            ("الأصول الثابتة والطويلة الأجل", [
                ("الأصول الثابتة (الإجمالي)", bs.fixed_assets),
                ("(-) مجمع الاستهلاك",        -bs.accumulated_depreciation),
                ("صافي الأصول الثابتة",       bs.net_fixed_assets),
                ("أصول طويلة الأجل أخرى",    bs.other_long_term_assets),
                ("إجمالي الأصول",             bs.total_assets),
            ], C["gold"]),
            ("الالتزامات المتداولة", [
                ("الذمم الدائنة",              bs.accounts_payable),
                ("ديون قصيرة الأجل",           bs.short_term_debt),
                ("التزامات متداولة أخرى",       bs.other_current_liabilities),
                ("إجمالي الالتزامات المتداولة", bs.current_liabilities),
            ], C["danger"]),
            ("الالتزامات طويلة الأجل", [
                ("ديون طويلة الأجل",           bs.long_term_debt),
                ("التزامات طويلة الأجل أخرى",  bs.other_long_term_liabilities),
                ("إجمالي الالتزامات",          bs.total_liabilities),
            ], C["warning"]),
            ("حقوق الملكية", [
                ("رأس المال المدفوع",          bs.paid_in_capital),
                ("الأرباح المحتجزة",           bs.retained_earnings),
                ("إجمالي حقوق الملكية",        bs.total_equity),
                ("إجمالي الالتزامات + حقوق الملكية", bs.total_liabilities_equity),
            ], C["success"]),
        ]

        row = 4
        for sec_title, items, color in sections:
            _section_header(ws, row, 1, 2, sec_title, color)
            row += 1
            for label, val in items:
                is_total = "إجمالي" in label or "صافي" in label
                bg = C["card"] if is_total else C["medium"]
                _cell(ws, row, 1, label, font=_font(10, is_total, C["light"]),
                      fill=_fill(bg), align=_align(), border=_border())
                _cell(ws, row, 2, val, font=_font(11, is_total, color if is_total else C["light"]),
                      fill=_fill(bg), align=_align("left"), border=_border(), fmt="#,##0.00")
                row += 1
            row += 1

        balanced = abs(bs.total_assets - bs.total_liabilities_equity) < 1
        ws.merge_cells(f"A{row}:B{row}")
        status = "✅ الميزانية متوازنة" if balanced else f"❌ فرق: {bs.total_assets - bs.total_liabilities_equity:,.0f}"
        _cell(ws, row, 1, status,
              font=_font(13, True, C["success"] if balanced else C["danger"]),
              fill=_fill(C["header"]), align=_align("center"))

        ws.column_dimensions["A"].width = 40
        ws.column_dimensions["B"].width = 24

    # ─── التدفقات النقدية ───
    if app.cashflow_data:
        cf = app.cashflow_data
        ws = wb.create_sheet("التدفقات النقدية")
        ws.sheet_view.rightToLeft = True
        _sheet_header(ws, "قائمة التدفقات النقدية — Cash Flow Statement", company, year, 2)

        sections_cf = [
            ("أنشطة التشغيل", [
                ("صافي الدخل",                  cf.net_income),
                ("الاستهلاك والإطفاء",          cf.depreciation_add_back),
                ("التغير في الذمم المدينة",      cf.change_in_receivables),
                ("التغير في المخزون",            cf.change_in_inventory),
                ("التغير في الذمم الدائنة",      cf.change_in_payables),
                ("تعديلات أخرى",                cf.other_operating),
                ("صافي التدفق التشغيلي",        cf.operating_cash_flow),
            ], C["success"]),
            ("أنشطة الاستثمار", [
                ("النفقات الرأسمالية CAPEX",    cf.capex),
                ("عائدات بيع أصول",             cf.asset_sales),
                ("استثمارات أخرى",              cf.other_investing),
                ("صافي التدفق الاستثماري",      cf.investing_cash_flow),
            ], C["warning"]),
            ("أنشطة التمويل", [
                ("اقتراض جديد",                 cf.debt_issued),
                ("سداد ديون",                   cf.debt_repaid),
                ("توزيعات أرباح",               cf.dividends_paid),
                ("إصدار أسهم",                  cf.equity_issued),
                ("صافي التدفق التمويلي",        cf.financing_cash_flow),
            ], C["accent"]),
            ("ملخص النقد", [
                ("رصيد النقد أول الفترة",       cf.beginning_cash),
                ("صافي التغير في النقد",        cf.net_change_in_cash),
                ("التدفق النقدي الحر FCF",      cf.free_cash_flow),
                ("رصيد النقد آخر الفترة",       cf.ending_cash),
            ], C["gold"]),
        ]

        row = 4
        for sec_title, items, color in sections_cf:
            _section_header(ws, row, 1, 2, sec_title, color)
            row += 1
            for label, val in items:
                is_total = "صافي" in label or "رصيد" in label or "حر" in label
                bg = C["card"] if is_total else C["medium"]
                v_color = color if is_total else (C["success"] if val >= 0 else C["danger"])
                _cell(ws, row, 1, label, font=_font(10, is_total, C["light"]),
                      fill=_fill(bg), align=_align(), border=_border())
                _cell(ws, row, 2, val, font=_font(11, is_total, v_color),
                      fill=_fill(bg), align=_align("left"), border=_border(), fmt="#,##0.00")
                row += 1
            row += 1

        ws.column_dimensions["A"].width = 38
        ws.column_dimensions["B"].width = 24

    # ─── النسب المالية + التحليلات المتقدمة ───
    if app.income_data and app.balance_data:
        from financial_engine import FinancialRatios
        ratios = FinancialRatios(app.income_data, app.balance_data, app.cashflow_data, getattr(app, 'sector', ''))
        all_ratios = ratios.get_all_ratios()
        interpretations = ratios.get_interpretation()

        ws = wb.create_sheet("النسب المالية")
        ws.sheet_view.rightToLeft = True
        _sheet_header(ws, "النسب المالية — Financial Ratios (Advanced Financial Analysis Framework)", company, year, 2)

        row = 4
        for category, items in all_ratios.items():
            _section_header(ws, row, 1, 3, category)
            row += 1
            _table_header(ws, row, ["النسبة", "القيمة", "المعيار"])
            row += 1

            benchmarks = {
                "نسبة التداول":                    (">= 2.0",  True),
                "نسبة السيولة السريعة":            (">= 1.0",  True),
                "هامش صافي الدخل %":               (">= 10%",  True),
                "العائد على حقوق الملكية ROE %":   (">= 15%",  True),
                "نسبة الدين إلى الأصول":           ("< 0.50",  False),
                "نسبة تغطية الفائدة":              (">= 3.0x", True),
                "معدل دوران الأصول":               (">= 0.5",  True),
            }

            for name, value in items.items():
                bench = benchmarks.get(name, ("—", True))
                _cell(ws, row, 1, name, font=_font(10, color=C["light"]),
                      fill=_fill(C["medium"]), align=_align(), border=_border())
                _cell(ws, row, 2, value, font=_font(11, True, C["accent"]),
                      fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="0.00")
                _cell(ws, row, 3, bench[0], font=_font(9, color=C["light"]),
                      fill=_fill(C["medium"]), align=_align("center"), border=_border())
                row += 1
            row += 1

        _section_header(ws, row, 1, 3, "التفسير والتوصيات — Advanced Financial Analysis Framework")
        row += 1
        for icon, category, note in interpretations:
            _cell(ws, row, 1, f"{icon} {category}", font=_font(10, True, C["gold"]),
                  fill=_fill(C["card"]), align=_align(), border=_border())
            ws.merge_cells(f"B{row}:C{row}")
            _cell(ws, row, 2, note, font=_font(9, color=C["light"]),
                  fill=_fill(C["medium"]), align=_align("right", wrap=True), border=_border())
            ws.row_dimensions[row].height = 30
            row += 1

        ws.column_dimensions["A"].width = 42
        ws.column_dimensions["B"].width = 16
        ws.column_dimensions["C"].width = 35

        # ─── تحليلات متقدمة ───
        ws_adv = wb.create_sheet("تحليلات متقدمة")
        ws_adv.sheet_view.rightToLeft = True
        _sheet_header(ws_adv, "التحليلات المتقدمة — DuPont | EVA | Altman Z-Score", company, year, 2)

        row = 4
        # DuPont
        _section_header(ws_adv, row, 1, 2, "تحليل DuPont — تفكيك ROE (3 عوامل + 5 عوامل)")
        row += 1
        dupont = ratios.dupont_analysis()
        for name, val in dupont.items():
            _cell(ws_adv, row, 1, name, font=_font(10, color=C["light"]),
                  fill=_fill(C["medium"]), align=_align(), border=_border())
            _cell(ws_adv, row, 2, val, font=_font(11, True, C["accent"]),
                  fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="0.0000")
            row += 1

        row += 1
        _section_header(ws_adv, row, 1, 2, "القيمة الاقتصادية المضافة EVA (WACC = 10%)")
        row += 1
        eva = ratios.economic_value_added(0.10)
        for name, val in eva.items():
            if name == "_color":
                continue
            _cell(ws_adv, row, 1, name, font=_font(10, color=C["light"]),
                  fill=_fill(C["medium"]), align=_align(), border=_border())
            if isinstance(val, str):
                color = C["success"] if "تخلق" in val else C["danger"]
                _cell(ws_adv, row, 2, val, font=_font(11, True, color),
                      fill=_fill(C["dark"]), align=_align("left"), border=_border())
            else:
                color = C["success"] if val > 0 else C["danger"]
                _cell(ws_adv, row, 2, val, font=_font(11, True, color),
                      fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="#,##0.00")
            row += 1

        row += 1
        _section_header(ws_adv, row, 1, 2, "Altman Z-Score — مؤشر التعثر المالي")
        row += 1
        z_data = ratios.altman_z_score()
        color_map = {"green": C["success"], "orange": C["warning"], "red": C["danger"]}
        z_color = color_map.get(z_data.get("_color", "green"), C["success"])
        for name, val in z_data.items():
            if name == "_color":
                continue
            _cell(ws_adv, row, 1, name, font=_font(10, color=C["light"]),
                  fill=_fill(C["medium"]), align=_align(), border=_border())
            if isinstance(val, str):
                _cell(ws_adv, row, 2, val, font=_font(11, True, z_color),
                      fill=_fill(C["dark"]), align=_align("left"), border=_border())
            else:
                c = z_color if name == "Z-Score" else C["accent"]
                _cell(ws_adv, row, 2, val, font=_font(11, True, c),
                      fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="0.0000")
            row += 1

        ws_adv.column_dimensions["A"].width = 48
        ws_adv.column_dimensions["B"].width = 28

    # ─── التقييم والمخاطر والتوصيات ───
    if app.income_data and app.balance_data:
        from financial_engine import FinancialScorecard, RiskAnalysis, SmartRecommendations

        inc = app.income_data
        bs  = app.balance_data
        cf  = getattr(app, "cashflow_data", None)

        # ─── ورقة Dashboard ───
        ws_dash = wb.create_sheet("لوحة المؤشرات")
        ws_dash.sheet_view.rightToLeft = True
        _sheet_header(ws_dash, "لوحة المؤشرات — Executive Dashboard", company, year, 4)

        scorecard = FinancialScorecard(inc, bs, cf).calculate()
        total_score = scorecard["التقييم_الإجمالي"]
        grade       = scorecard["التصنيف"]
        desc        = scorecard["الوصف"]
        score_color = C["success"] if total_score >= 80 else (C["warning"] if total_score >= 60 else C["danger"])

        ws_dash.merge_cells("A4:D4")
        _cell(ws_dash, 4, 1,
              f"FYQ Financial Score: {total_score} / 100 — {grade} ({desc})",
              font=_font(14, True, score_color), fill=_fill(C["header"]), align=_align("center"))
        ws_dash.row_dimensions[4].height = 28

        row = 6
        _section_header(ws_dash, row, 1, 4, "محاور التقييم")
        row += 1
        _table_header(ws_dash, row, ["المحور", "الدرجة", "من", "النسبة"])
        row += 1
        for axis, data in scorecard["المحاور"].items():
            s = data["الدرجة"]; m = data["من"]
            pct = s / m
            c = C["success"] if pct >= 0.75 else (C["warning"] if pct >= 0.5 else C["danger"])
            _cell(ws_dash, row, 1, axis, font=_font(10, color=C["light"]),
                  fill=_fill(C["medium"]), align=_align(), border=_border())
            _cell(ws_dash, row, 2, s, font=_font(11, True, c),
                  fill=_fill(C["dark"]), align=_align("center"), border=_border(), fmt="0")
            _cell(ws_dash, row, 3, m, font=_font(10, color=C["light"]),
                  fill=_fill(C["dark"]), align=_align("center"), border=_border(), fmt="0")
            _cell(ws_dash, row, 4, pct, font=_font(11, True, c),
                  fill=_fill(C["dark"]), align=_align("center"), border=_border(), fmt="0%")
            row += 1

        row += 1
        _section_header(ws_dash, row, 1, 4, "مؤشرات الأداء الرئيسية")
        row += 1
        kpi_items = [
            ("الإيرادات",                     inc.revenue),
            ("EBITDA",                          inc.ebitda),
            ("صافي الدخل",                   inc.net_income),
            ("هامش صافي الدخل %",                inc.net_margin),
            ("إجمالي الأصول",               bs.total_assets),
            ("حقوق الملكية",                bs.total_equity),
        ]
        if cf:
            kpi_items += [
                ("التدفق التشغيلي",           cf.operating_cash_flow),
                ("FCF",                             cf.free_cash_flow),
            ]
        _table_header(ws_dash, row, ["المؤشر", "القيمة", "العملة", "ملاحظة"])
        row += 1
        for name, val in kpi_items:
            c = C["success"] if val >= 0 else C["danger"]
            _cell(ws_dash, row, 1, name, font=_font(10, color=C["light"]),
                  fill=_fill(C["medium"]), align=_align(), border=_border())
            _cell(ws_dash, row, 2, val, font=_font(11, True, c),
                  fill=_fill(C["dark"]), align=_align("left"), border=_border(), fmt="#,##0.00")
            _cell(ws_dash, row, 3, currency, font=_font(9, color=C["light"]),
                  fill=_fill(C["dark"]), align=_align("center"), border=_border())
            _cell(ws_dash, row, 4, "", fill=_fill(C["dark"]), border=_border())
            row += 1

        for col_letter, width in [("A", 38), ("B", 20), ("C", 12), ("D", 14)]:
            ws_dash.column_dimensions[col_letter].width = width

        # ─── ورقة المخاطر ───
        ws_risk = wb.create_sheet("تحليل المخاطر")
        ws_risk.sheet_view.rightToLeft = True
        _sheet_header(ws_risk, "تحليل المخاطر المالية — Risk Analysis", company, year, 4)

        risk_engine = RiskAnalysis(inc, bs, cf)
        risks = risk_engine.get_all_risks()
        overall = risk_engine.overall_risk_level()
        overall_color = {"منخفض": C["success"], "متوسط": C["warning"], "مرتفع": C["danger"]}[overall]

        ws_risk.merge_cells("A4:D4")
        _cell(ws_risk, 4, 1, f"مستوى المخاطر الإجمالي: {overall}",
              font=_font(14, True, overall_color), fill=_fill(C["header"]), align=_align("center"))
        ws_risk.row_dimensions[4].height = 28

        row = 6
        _table_header(ws_risk, row, ["المخاطرة", "المستوى", "الدرجة/100", "الوصف"])
        row += 1
        for risk in risks:
            level = risk["المستوى"]
            c = {"منخفض": C["success"], "متوسط": C["warning"], "مرتفع": C["danger"]}[level]
            _cell(ws_risk, row, 1, f"{risk['icon']} {risk['المخاطرة']}",
                  font=_font(10, True, c), fill=_fill(C["medium"]), align=_align(), border=_border())
            _cell(ws_risk, row, 2, level, font=_font(10, True, c),
                  fill=_fill(C["dark"]), align=_align("center"), border=_border())
            _cell(ws_risk, row, 3, risk["الدرجة"], font=_font(11, True, c),
                  fill=_fill(C["dark"]), align=_align("center"), border=_border(), fmt="0")
            _cell(ws_risk, row, 4, risk["الوصف"], font=_font(9, color=C["light"]),
                  fill=_fill(C["dark"]), align=_align("right", wrap=True), border=_border())
            ws_risk.row_dimensions[row].height = 28
            row += 1

        for col_letter, width in [("A", 28), ("B", 14), ("C", 12), ("D", 55)]:
            ws_risk.column_dimensions[col_letter].width = width

        # ─── ورقة التوصيات ───
        ws_rec = wb.create_sheet("التوصيات")
        ws_rec.sheet_view.rightToLeft = True
        _sheet_header(ws_rec, "التوصيات الذكية — Smart Recommendations", company, year, 4)

        smart = SmartRecommendations(inc, bs, cf)
        recs  = smart.get_recommendations()

        row = 4
        _table_header(ws_rec, row, ["الأولوية", "الفئة", "التوصية", "الأثر المتوقع"])
        row += 1
        priority_labels = {1: ("🔴 عاجل", C["danger"]), 2: ("🟡 مهم", C["warning"]), 3: ("🟢 تحسين", C["success"])}
        for priority, category, title, rec, impact in recs:
            p_label, p_color = priority_labels.get(priority, ("ℹ️", C["light"]))
            _cell(ws_rec, row, 1, p_label, font=_font(10, True, p_color),
                  fill=_fill(C["medium"]), align=_align("center"), border=_border())
            _cell(ws_rec, row, 2, category, font=_font(10, color=C["gold"]),
                  fill=_fill(C["medium"]), align=_align(), border=_border())
            _cell(ws_rec, row, 3, f"{title}: {rec}", font=_font(10, color=C["light"]),
                  fill=_fill(C["dark"]), align=_align("right", wrap=True), border=_border())
            _cell(ws_rec, row, 4, impact, font=_font(9, color=C["teal"]),
                  fill=_fill(C["dark"]), align=_align("right", wrap=True), border=_border())
            ws_rec.row_dimensions[row].height = 35
            row += 1

        for col_letter, width in [("A", 14), ("B", 18), ("C", 60), ("D", 35)]:
            ws_rec.column_dimensions[col_letter].width = width

        # ─── تحديث بيانات الغلاف ───
        sector    = getattr(app, "sector",        "") or ""
        preparer  = getattr(app, "preparer_name", "") or ""
        rep_date  = getattr(app, "report_date",   now_str) or now_str
        trade_reg = getattr(app, "trade_register","") or ""

        if sector:
            ws_cover.merge_cells("A6:F6")
            _cell(ws_cover, 6, 1, f"القطاع: {sector}",
                  font=_font(11, color=C["light"]), fill=_fill(C["dark"]), align=_align("center"))
        if trade_reg:
            ws_cover.merge_cells("A9:F9")
            _cell(ws_cover, 9, 1, f"السجل التجاري: {trade_reg}",
                  font=_font(10, color=C["border"]), fill=_fill(C["dark"]), align=_align("center"))
        if preparer:
            ws_cover.merge_cells("A11:F11")
            _cell(ws_cover, 11, 1, f"معد التقرير: {preparer} | تاريخ التقرير: {rep_date}",
                  font=_font(10, color=C["border"]), fill=_fill(C["dark"]), align=_align("center"))

    wb.save(output_path)


# ─────────────────────────────────────────────
#  دوال مساعدة
# ─────────────────────────────────────────────

def _sheet_header(ws, title: str, company: str, year: str, cols: int = 2):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=cols)
    _cell(ws, 1, 1, title, font=_font(14, True, C["gold"]),
          fill=_fill(C["header"]), align=_align("center"))

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=cols)
    _cell(ws, 2, 1, f"{company} | السنة المالية: {year} | {datetime.now().strftime('%Y-%m-%d')}",
          font=_font(10, color=C["light"]), fill=_fill(C["card"]), align=_align("center"))

    ws.row_dimensions[1].height = 28
    ws.row_dimensions[2].height = 18

def _table_header(ws, row: int, labels: list):
    for col, label in enumerate(labels, 1):
        _cell(ws, row, col, label, font=_font(10, True, C["gold"]),
              fill=_fill(C["card"]), align=_align("center"), border=_border())
    ws.row_dimensions[row].height = 20
