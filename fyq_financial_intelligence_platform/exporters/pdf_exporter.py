"""
FYQ - تصدير تقارير PDF الاحترافية
FYQ - Professional PDF Report Exporter
معايير Advanced Financial Analysis
"""

import os
import re
from core.financial_engine import (
    FinancialScorecard,
    RiskAnalysis,
    SmartRecommendations
)
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph as RLParagraph, Spacer, Table as RLTable, TableStyle,
        HRFlowable, PageBreak, KeepTogether
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False



# Arabic shaping is applied before ReportLab layout. Without it, some Linux PDF
# viewers render Arabic as disconnected glyphs or tofu boxes.
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_SHAPING = True
except ImportError:
    HAS_ARABIC_SHAPING = False

_ARABIC_RUN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF][\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s،؛؟ـ]*')

def _shape_arabic(value):
    if not isinstance(value, str) or not HAS_ARABIC_SHAPING:
        return value
    def repl(match):
        raw = match.group(0)
        # Preserve surrounding whitespace outside bidi transformation.
        left = raw[:len(raw)-len(raw.lstrip())]
        right = raw[len(raw.rstrip()):]
        core = raw.strip()
        if not core:
            return raw
        return left + get_display(arabic_reshaper.reshape(core)) + right
    return _ARABIC_RUN.sub(repl, value)

def Paragraph(text, style, *args, **kwargs):
    return RLParagraph(_shape_arabic(text), style, *args, **kwargs)

def _shape_table_cell(cell):
    if isinstance(cell, str):
        return _shape_arabic(cell)
    return cell

def Table(data, *args, **kwargs):
    shaped = [[_shape_table_cell(cell) for cell in row] for row in data]
    return RLTable(shaped, *args, **kwargs)

_PDF_KPI_LABELS = {
    "هامش المبيعات الإجمالي %": "هامش مجمل الربح %",
    "هامش EBITDA %": "هامش الأرباح قبل الفوائد والضرائب والاستهلاك والإطفاء %",
    "هامش التشغيل %": "هامش الربح التشغيلي %",
    "هامش صافي الدخل %": "هامش صافي الدخل %",
    "العائد على الأصول ROA %": "العائد على الأصول %",
    "العائد على حقوق الملكية ROE %": "العائد على حقوق الملكية %",
    "العائد على رأس المال ROIC %": "العائد على رأس المال المستثمر %",
    "العائد على رأس المال المستخدم ROCE %": "العائد على رأس المال المستخدم %",
    "صافي الدين إلى EBITDA (مرة)": "صافي الدين إلى الأرباح قبل الفوائد والضرائب والاستهلاك والإطفاء (مرة)",
    "ROE": "العائد على حقوق الملكية",
    "ROA": "العائد على الأصول",
    "هامش EBITDA": "هامش الأرباح قبل الفوائد والضرائب والاستهلاك والإطفاء",
    "الدين/الأصول": "نسبة الدين إلى الأصول",
}

def _pdf_kpi_label(name):
    label = _PDF_KPI_LABELS.get(name, name)
    return label if str(label).strip() else "مؤشر غير مسمى"

# ─────────────────────────────────────────────
#  الألوان
# ─────────────────────────────────────────────
DARK    = HexColor("#07111F")
MEDIUM  = HexColor("#0D1B2A")
CARD    = HexColor("#13263A")
GOLD    = HexColor("#C9A45C")
ACCENT  = HexColor("#2F6FED")
SUCCESS = HexColor("#2EA043")
DANGER  = HexColor("#DA3633")
WARNING = HexColor("#D29922")
LIGHT   = HexColor("#F4F7FB")
DIM     = HexColor("#667085")
PURPLE  = HexColor("#8957E5")
TEAL    = HexColor("#39D353")
BORDER  = HexColor("#D6DEE8")
PAPER   = HexColor("#F7F8FA")
INK     = HexColor("#152238")


def _register_fonts():
    """تسجيل خطوط عربية"""
    local_fonts = os.path.join(os.path.dirname(__file__), "static", "fonts")
    font_paths = [
        (os.path.join(local_fonts, "NotoSansArabic-Regular.ttf"), "NotoArabic"),
        (os.path.join(local_fonts, "NotoSansArabic-Bold.ttf"),    "NotoArabicBold"),
        ("/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf", "NotoArabic"),
        ("/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",    "NotoArabicBold"),
        ("/usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Regular.ttf", "Amiri"),
        ("/usr/share/fonts/opentype/fonts-hosny-amiri/Amiri-Bold.ttf",    "AmiriBold"),
    ]
    registered = []
    for path, name in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered.append(name)
            except Exception:
                pass
    return registered


def _get_styles(arabic_font="Helvetica", arabic_bold="Helvetica-Bold"):
    """إنشاء أنماط النصوص"""
    styles = {
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=26, textColor=GOLD,
            alignment=TA_CENTER, spaceAfter=6, leading=28,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName=arabic_font, fontSize=13, textColor=INK,
            alignment=TA_CENTER, spaceAfter=4, leading=18,
        ),
        "section": ParagraphStyle(
            "section", fontName=arabic_bold, fontSize=15, textColor=HexColor("#B88912"),
            alignment=TA_RIGHT, spaceBefore=8, spaceAfter=5, leading=20,
        ),
        "body": ParagraphStyle(
            "body", fontName=arabic_font, fontSize=10, textColor=INK,
            alignment=TA_RIGHT, spaceAfter=4, leading=15,
        ),
        "body_bold": ParagraphStyle(
            "body_bold", fontName=arabic_bold, fontSize=10, textColor=INK,
            alignment=TA_RIGHT, spaceAfter=4, leading=15,
        ),
        "small": ParagraphStyle(
            "small", fontName=arabic_font, fontSize=8, textColor=DIM,
            alignment=TA_CENTER, spaceAfter=2, leading=12,
        ),
        "kpi_val": ParagraphStyle(
            "kpi_val", fontName=arabic_bold, fontSize=16, textColor=GOLD,
            alignment=TA_CENTER, leading=20,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label", fontName=arabic_font, fontSize=8, textColor=DIM,
            alignment=TA_CENTER, leading=11,
        ),
        "success": ParagraphStyle(
            "success", fontName=arabic_font, fontSize=10, textColor=SUCCESS,
            alignment=TA_RIGHT, spaceAfter=3, leading=15,
        ),
        "danger": ParagraphStyle(
            "danger", fontName=arabic_font, fontSize=10, textColor=DANGER,
            alignment=TA_RIGHT, spaceAfter=3, leading=15,
        ),
        "warning_style": ParagraphStyle(
            "warning_style", fontName=arabic_font, fontSize=10, textColor=WARNING,
            alignment=TA_RIGHT, spaceAfter=3, leading=15,
        ),
    }
    return styles


def _table_style_base(header_color=ACCENT):
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  header_color),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  GOLD),
        ("FONTNAME",      (0, 0), (-1, 0),  "NotoArabicBold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  9),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [MEDIUM, CARD]),
        ("TEXTCOLOR",     (0, 1), (-1, -1), LIGHT),
        ("FONTNAME",      (0, 1), (-1, -1), "NotoArabic"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("ALIGN",         (0, 1), (-1, -1), "RIGHT"),
        ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ])



def _score_methodology_table(scorecard, arabic_font, arabic_bold, width):
    """Compact score governance block without mixed-direction prose."""
    version = scorecard.get("إصدار_المنهجية", "FYQ-SCORE")
    tests = scorecard.get("عدد_الاختبارات", 0)
    rows = [
        [Paragraph("المنهجية", ParagraphStyle("smk1", fontName=arabic_bold, fontSize=8, textColor=DIM, alignment=TA_RIGHT, leading=11)),
         RLParagraph(str(version), ParagraphStyle("smv1", fontName="Helvetica-Bold", fontSize=8, textColor=INK, alignment=TA_CENTER, leading=11)),
         Paragraph("الاختبارات الكمية", ParagraphStyle("smk2", fontName=arabic_bold, fontSize=8, textColor=DIM, alignment=TA_RIGHT, leading=11)),
         RLParagraph(str(tests), ParagraphStyle("smv2", fontName="Helvetica-Bold", fontSize=8, textColor=INK, alignment=TA_CENTER, leading=11))],
        [Paragraph("الأوزان", ParagraphStyle("smk3", fontName=arabic_bold, fontSize=8, textColor=DIM, alignment=TA_RIGHT, leading=11)),
         Paragraph("السيولة 20% | الربحية 25% | الكفاءة 20% | المديونية 20% | التدفقات 15%", ParagraphStyle("smv3", fontName=arabic_font, fontSize=7.6, textColor=INK, alignment=TA_CENTER, leading=11)),
         Paragraph("نوع القراءة", ParagraphStyle("smk4", fontName=arabic_bold, fontSize=8, textColor=DIM, alignment=TA_RIGHT, leading=11)),
         Paragraph("تشخيص أداء داخلي — ليس تصنيفًا ائتمانيًا", ParagraphStyle("smv4", fontName=arabic_font, fontSize=7.6, textColor=INK, alignment=TA_CENTER, leading=11))],
    ]
    t = Table(rows, colWidths=[width*0.13, width*0.27, width*0.16, width*0.44])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("BOX", (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID", (0,0), (-1,-1), 0.35, BORDER),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return t

def _score_banner(total_score, grade, desc, provisional, score_color, arabic_font, arabic_bold, width):
    """Render score metadata in isolated cells to avoid Arabic/Latin bidi collisions."""
    if provisional:
        text = Paragraph(f"التقييم النهائي محجوب — {desc}", ParagraphStyle(
            "score_blocked", fontName=arabic_bold, fontSize=13, textColor=score_color, alignment=TA_CENTER, leading=19))
        t = Table([[text]], colWidths=[width])
    else:
        label = Paragraph("درجة التشخيص المالي", ParagraphStyle(
            "score_label_ar", fontName=arabic_bold, fontSize=10, textColor=DIM, alignment=TA_CENTER, leading=14))
        score = RLParagraph(f"<b>{total_score}</b><font size=9> / 100</font>", ParagraphStyle(
            "score_num", fontName="Helvetica-Bold", fontSize=18, textColor=score_color, alignment=TA_CENTER, leading=20))
        band = RLParagraph(f"<b>{grade}</b>", ParagraphStyle(
            "score_band", fontName="Helvetica-Bold", fontSize=13, textColor=score_color, alignment=TA_CENTER, leading=17))
        desc_p = Paragraph(desc, ParagraphStyle(
            "score_desc_ar", fontName=arabic_bold, fontSize=10, textColor=INK, alignment=TA_CENTER, leading=14))
        t = Table([[label, score, band, desc_p]], colWidths=[width*0.30, width*0.20, width*0.14, width*0.36])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("BOX", (0,0), (-1,-1), 0.8, score_color),
        ("INNERGRID", (0,0), (-1,-1), 0.4, BORDER),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    return t

def _page_header_footer(canvas, doc, company, year, page_num, total_pages):
    """هوية صفحات تقرير FYQ الرسمية."""
    canvas.saveState()
    w, h = A4

    # الغلاف مستقل بصرياً عن الصفحات الداخلية
    if page_num == 1:
        canvas.setFillColor(DARK)
        canvas.rect(0, 0, w, h, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, h - 4*mm, w, 4*mm, fill=1, stroke=0)
        canvas.setFillColor(ACCENT)
        canvas.rect(0, 0, 16*mm, h, fill=1, stroke=0)
        canvas.restoreState()
        return

    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    # هيدر مؤسسي
    canvas.setFillColor(DARK)
    canvas.rect(0, h - 17*mm, w, 17*mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 17*mm, w, 1.2, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 9.5)
    canvas.setFillColor(white)
    canvas.drawRightString(w - 12*mm, h - 10.5*mm, "FYQ Financial Intelligence Platform")
    canvas.setFont("NotoArabic", 8)
    canvas.setFillColor(HexColor("#B7C3D4"))
    canvas.drawString(12*mm, h - 10.5*mm, _shape_arabic(f"{company}  |  {year}"))

    # تذييل موحّد: هوية المنصة وحقوق الملكية ورقم الصفحة
    canvas.setStrokeColor(HexColor("#D6DEE8"))
    canvas.setLineWidth(0.6)
    canvas.line(12*mm, 13*mm, w - 12*mm, 13*mm)
    canvas.setFont("Helvetica", 6.8)
    canvas.setFillColor(DIM)
    canvas.drawString(12*mm, 7.5*mm, "FYQ Financial Intelligence Platform | Developed by SANAD ALANZI")
    canvas.setFont("NotoArabicBold", 8)
    canvas.setFillColor(INK)
    canvas.drawRightString(w - 12*mm, 7.5*mm, str(page_num - 1))
    canvas.restoreState()


def export_pdf_report(app, output_path: str):
    """تصدير تقرير PDF احترافي شامل"""
    if not HAS_REPORTLAB:
        raise ImportError(
            "مكتبة reportlab غير مثبتة.\n"
            "نفّذ: pip install reportlab"
        )

    company   = getattr(app, "company_name",   "شركة نموذجية") or "شركة نموذجية"
    year      = getattr(app, "fiscal_year",    str(datetime.now().year)) or str(datetime.now().year)
    currency  = getattr(app, "currency",       "ريال") or "ريال"
    sector    = getattr(app, "sector",         "") or ""
    preparer  = getattr(app, "preparer_name",  "") or ""
    rep_date  = getattr(app, "report_date",    datetime.now().strftime("%Y-%m-%d")) or datetime.now().strftime("%Y-%m-%d")
    trade_reg = getattr(app, "trade_register", "") or ""
    now_str   = datetime.now().strftime("%Y-%m-%d")

    # تسجيل الخطوط
    registered = _register_fonts()
    if "NotoArabic" in registered:
        arabic_font = "NotoArabic"
        arabic_bold = "NotoArabicBold" if "NotoArabicBold" in registered else "NotoArabic"
    elif "Amiri" in registered:
        arabic_font = "Amiri"
        arabic_bold = "AmiriBold" if "AmiriBold" in registered else "Amiri"
    else:
        arabic_font = "Helvetica"
        arabic_bold = "Helvetica-Bold"

    styles = _get_styles(arabic_font, arabic_bold)

    # حساب عدد الصفحات مسبقاً (تقدير)
    story = []
    page_counter = [0]
    total_pages_est = [1]

    def on_page(canvas, doc):
        page_counter[0] += 1
        _page_header_footer(canvas, doc, company, year,
                            page_counter[0], total_pages_est[0])

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=2.0*cm, bottomMargin=1.8*cm,
        title=f"FYQ Financial Intelligence Platform — التقرير المالي {company} {year}",
        author="SANAD ALANZI",
        subject="FYQ Financial Intelligence Platform | تقرير الأداء المالي والقرارات التنفيذية",
    )

    W = A4[0] - 3.6*cm  # عرض المحتوى

    # ─────────────────────────────────────────────
    #  صفحة الغلاف — Executive institutional cover
    # ─────────────────────────────────────────────
    cover_title = ParagraphStyle("cover_title", fontName="Helvetica-Bold", fontSize=30, textColor=white, alignment=TA_CENTER, leading=38)
    cover_sub = ParagraphStyle("cover_sub", fontName="Helvetica", fontSize=12, textColor=HexColor("#B7C3D4"), alignment=TA_CENTER, leading=18)
    cover_company = ParagraphStyle("cover_company", fontName=arabic_bold, fontSize=21, textColor=white, alignment=TA_CENTER, leading=28)
    cover_meta = ParagraphStyle("cover_meta", fontName=arabic_font, fontSize=9, textColor=HexColor("#D8E0EA"), alignment=TA_CENTER, leading=14)

    story.append(Spacer(1, 3.2*cm))
    story.append(Paragraph("FYQ", cover_title))
    story.append(Paragraph("FINANCIAL INTELLIGENCE PLATFORM", cover_sub))
    story.append(Spacer(1, 1.0*cm))
    story.append(HRFlowable(width=W*0.56, thickness=1.4, color=GOLD))
    story.append(Spacer(1, 0.9*cm))
    story.append(Paragraph(company, cover_company))
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph(f"التقرير المالي التنفيذي | السنة المالية {year}", ParagraphStyle("cover_ar", fontName=arabic_font, fontSize=12, textColor=HexColor("#B7C3D4"), alignment=TA_CENTER, leading=18)))
    if sector:
        sector_row = Table([[
            Paragraph("القطاع", cover_meta),
            Paragraph(str(sector), ParagraphStyle("cover_sector_value", fontName="Helvetica", fontSize=9, textColor=HexColor("#D8E0EA"), alignment=TA_CENTER, leading=14)),
        ]], colWidths=[W*0.12, W*0.22], hAlign="CENTER")
        sector_row.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("LEFTPADDING", (0,0), (-1,-1), 2),
            ("RIGHTPADDING", (0,0), (-1,-1), 2),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        story.append(sector_row)
    if trade_reg:
        story.append(Paragraph(f"السجل التجاري: {trade_reg}", cover_meta))
    story.append(Spacer(1, 1.0*cm))

    meta_rows = [
        [Paragraph("تاريخ التقرير", cover_meta), Paragraph(str(rep_date), cover_meta)],
        [Paragraph("تاريخ الإصدار", cover_meta), Paragraph(str(now_str), cover_meta)],
    ]
    if preparer:
        meta_rows.insert(0, [Paragraph("إعداد", cover_meta), Paragraph(preparer, cover_meta)])
    meta_table = Table(meta_rows, colWidths=[W*0.28, W*0.28])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HexColor("#0D1B2A")),
        ("BOX", (0,0), (-1,-1), 0.7, HexColor("#31455E")),
        ("INNERGRID", (0,0), (-1,-1), 0.4, HexColor("#31455E")),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 1.2*cm))
    story.append(Paragraph("EXECUTIVE FINANCIAL PERFORMANCE REPORT", ParagraphStyle(
        "cover_mark", fontName="Helvetica-Bold", fontSize=8.5, textColor=GOLD, alignment=TA_CENTER, leading=12)))
    story.append(PageBreak())

    # ─────────────────────────────────────────────
    #  فهرس المحتويات
    # ─────────────────────────────────────────────
    story.append(Paragraph("فهرس المحتويات", styles["section"]))
    story.append(HRFlowable(width=W, thickness=1, color=GOLD))
    story.append(Spacer(1, 0.3*cm))

    toc_items = [
        ("1", "الملخص التنفيذي"),
        ("2", "قائمة الدخل"),
        ("3", "الميزانية العمومية"),
        ("4", "قائمة التدفقات النقدية"),
        ("5", "النسب والمؤشرات المالية"),
        ("6", "تحليلات القيمة والكفاءة المتقدمة"),
        ("7", "التقييم المالي الشامل"),
        ("8", "تحليل المخاطر المالية"),
        ("9", "الأولويات والتوصيات التنفيذية"),
    ]
    toc_text_style = ParagraphStyle(
        "toc_text", fontName=arabic_bold, fontSize=11, textColor=HexColor("#111827"),
        alignment=TA_RIGHT, leading=17, spaceAfter=0
    )
    toc_num_style = ParagraphStyle(
        "toc_num", fontName=arabic_bold, fontSize=11, textColor=HexColor("#B88912"),
        alignment=TA_CENTER, leading=17, spaceAfter=0
    )
    toc_data = [[Paragraph(title, toc_text_style), Paragraph(num, toc_num_style)] for num, title in toc_items]
    toc_table = Table(toc_data, colWidths=[W * 0.88, W * 0.12])
    toc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), white),
        ("FONTNAME",      (0, 0), (-1, -1), arabic_font),
        ("ALIGN",         (0, 0), (0, -1),  "RIGHT"),
        ("ALIGN",         (1, 0), (1, -1),  "CENTER"),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.8, HexColor("#D9E1EA")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 0.45*cm))

    inc = getattr(app, "income_data", None)
    bs  = getattr(app, "balance_data", None)
    cf  = getattr(app, "cashflow_data", None)

    # Unified integrity gate used by executive, ratios, advanced analytics and risk.
    cash_gap = (bs.cash - cf.ending_cash) if (bs and cf) else 0
    cash_tolerance = max(1.0, abs(bs.cash) * 0.0001) if bs else 1.0
    cash_reconciled = (not cf) or abs(cash_gap) <= cash_tolerance
    ni_gap = (cf.net_income - inc.net_income) if (inc and cf) else 0
    ni_tolerance = max(1.0, abs(inc.net_income) * 0.0001) if inc else 1.0
    ni_reconciled = (not cf) or abs(ni_gap) <= ni_tolerance
    integrity_ok = bool(bs and bs.is_balanced and cash_reconciled and ni_reconciled)

    # ─────────────────────────────────────────────
    #  1. الملخص التنفيذي
    # ─────────────────────────────────────────────
    if inc and bs:
        story.append(PageBreak())
        story.append(Paragraph("1. الملخص التنفيذي", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=GOLD))
        story.append(Spacer(1, 0.3*cm))

        scorecard = FinancialScorecard(inc, bs, cf).calculate()
        total_score = scorecard["التقييم_الإجمالي"]
        grade       = scorecard["التصنيف"]
        desc        = scorecard["الوصف"]
        provisional = (scorecard.get("حالة_التقييم") == "PROVISIONAL") or (not integrity_ok)
        if not integrity_ok:
            desc = "سلامة القوائم تحتاج مراجعة"
        score_color = WARNING if provisional else (SUCCESS if total_score >= 80 else (WARNING if total_score >= 60 else DANGER))

        story.append(_score_banner(total_score, grade, desc, provisional, score_color, arabic_font, arabic_bold, W))
        story.append(_score_methodology_table(scorecard, arabic_font, arabic_bold, W))
        story.append(Spacer(1, 0.3*cm))

        # KPIs في جدول
        kpi_label_dark = ParagraphStyle("kpi_label_dark", fontName=arabic_font, fontSize=10, textColor=LIGHT, alignment=TA_RIGHT, leading=14)
        kpi_data = [
            ["المؤشر", "القيمة", "المؤشر", "القيمة"],
            [Paragraph("الإيرادات", kpi_label_dark),
             Paragraph(f"{inc.revenue:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=ACCENT, alignment=TA_LEFT, leading=14)),
             Paragraph("EBITDA", ParagraphStyle("kpi_en", fontName="Helvetica", fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=14)),
             Paragraph(f"{inc.ebitda:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=TEAL, alignment=TA_LEFT, leading=14))],
            [Paragraph("مجمل الربح", kpi_label_dark),
             Paragraph(f"{inc.gross_profit:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=SUCCESS, alignment=TA_LEFT, leading=14)),
             Paragraph("صافي الدخل", kpi_label_dark),
             Paragraph(f"{inc.net_income:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=GOLD, alignment=TA_LEFT, leading=14))],
            [Paragraph("إجمالي الأصول", kpi_label_dark),
             Paragraph(f"{bs.total_assets:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=ACCENT, alignment=TA_LEFT, leading=14)),
             Paragraph("حقوق الملكية", kpi_label_dark),
             Paragraph(f"{bs.total_equity:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=SUCCESS, alignment=TA_LEFT, leading=14))],
        ]
        if cf:
            kpi_data.append([
                Paragraph("التدفق التشغيلي", kpi_label_dark),
                Paragraph(f"{cf.operating_cash_flow:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=TEAL, alignment=TA_LEFT, leading=14)),
                Paragraph("FCF", ParagraphStyle("kpi_fcf", fontName="Helvetica", fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=14)),
                Paragraph(f"{cf.free_cash_flow:,.0f} {currency}", ParagraphStyle("v", fontName=arabic_bold, fontSize=10, textColor=SUCCESS if cf.free_cash_flow >= 0 else DANGER, alignment=TA_LEFT, leading=14)),
            ])

        kpi_table = Table(kpi_data, colWidths=[W*0.25, W*0.25, W*0.25, W*0.25])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  ACCENT),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  GOLD),
            ("FONTNAME",      (0, 0), (-1, 0),  arabic_bold),
            ("FONTSIZE",      (0, 0), (-1, 0),  9),
            ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [MEDIUM, CARD]),
            ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.3*cm))

        # الهوامش — خلايا مستقلة لمنع تشوه RTL/LTR أو سقوط اسم EBITDA
        margin_ar = ParagraphStyle("margin_ar", fontName=arabic_bold, fontSize=9, textColor=INK, alignment=TA_CENTER, leading=13)
        margin_en = ParagraphStyle("margin_en", fontName="Helvetica-Bold", fontSize=8.5, textColor=INK, alignment=TA_CENTER, leading=13)
        margin_cells = [[
            Paragraph(f"هامش مجمل الربح<br/>{inc.gross_margin:.1f}%", margin_ar),
            Paragraph(f"EBITDA Margin<br/>{inc.ebitda_margin:.1f}%", margin_en),
            Paragraph(f"هامش الربح التشغيلي<br/>{inc.operating_margin:.1f}%", margin_ar),
            Paragraph(f"هامش صافي الدخل<br/>{inc.net_margin:.1f}%", margin_ar),
        ]]
        margin_table = Table(margin_cells, colWidths=[W*0.25]*4)
        margin_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), HexColor("#F5F7FA")),
            ("BOX", (0,0), (-1,-1), 0.5, HexColor("#D6DEE8")),
            ("INNERGRID", (0,0), (-1,-1), 0.4, HexColor("#D6DEE8")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(margin_table)
        story.append(Spacer(1, 0.35*cm))

    # ─────────────────────────────────────────────
    #  2. قائمة الدخل
    # ─────────────────────────────────────────────
    if inc:
        story.append(Paragraph("2. قائمة الدخل — Income Statement", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=SUCCESS))
        story.append(Spacer(1, 0.3*cm))

        rows = [
            ("الإيرادات",                      inc.revenue,             LIGHT,   True),
            ("(-) تكلفة البضاعة المباعة",      -inc.cost_of_goods_sold, DANGER,  False),
            ("= مجمل الربح (Gross Profit)",    inc.gross_profit,        SUCCESS, True),
            ("(-) المصاريف التشغيلية",         -inc.operating_expenses, DANGER,  False),
            ("= EBITDA",                        inc.ebitda,              ACCENT,  True),
            ("(-) الاستهلاك والإطفاء",         -inc.depreciation,       WARNING, False),
            ("= ربح التشغيل EBIT",              inc.ebit,                ACCENT,  True),
            ("(-) مصاريف الفائدة",             -inc.interest_expense,   DANGER,  False),
            ("= الربح قبل الضريبة EBT",         inc.ebt,                 ACCENT,  True),
            ("(-) ضريبة الدخل",                -inc.tax,                DANGER,  False),
            ("= صافي الدخل (Net Income)",       inc.net_income,          GOLD,    True),
        ]

        inc_data = [["البند", f"القيمة ({currency})", "النسبة من الإيرادات"]]
        for label, val, color, bold in rows:
            pct = (val / inc.revenue * 100) if inc.revenue else 0
            fn = arabic_bold if bold else arabic_font
            label_flowable = (
                RLParagraph("EBITDA", ParagraphStyle("r_en_ebitda", fontName="Helvetica-Bold", fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13))
                if label == "= EBITDA" else
                Paragraph(label, ParagraphStyle("r", fontName=fn, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13))
            )
            inc_data.append([
                label_flowable,
                Paragraph(f"{val:,.0f}", ParagraphStyle("v", fontName=fn, fontSize=9, textColor=color, alignment=TA_LEFT, leading=13)),
                Paragraph(f"{pct:.1f}%", ParagraphStyle("p", fontName=fn, fontSize=9, textColor=color, alignment=TA_CENTER, leading=13)),
            ])

        inc_table = Table(inc_data, colWidths=[W*0.5, W*0.3, W*0.2])
        inc_table.setStyle(_table_style_base(SUCCESS))
        story.append(inc_table)
        story.append(Spacer(1, 0.35*cm))

    # ─────────────────────────────────────────────
    #  3. الميزانية العمومية
    # ─────────────────────────────────────────────
    if bs:
        story.append(Paragraph("3. الميزانية العمومية — Balance Sheet", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=ACCENT))
        story.append(Spacer(1, 0.3*cm))

        bs_sections = [
            ("الأصول المتداولة", [
                ("النقد وما في حكمه",        bs.cash),
                ("الذمم المدينة",             bs.accounts_receivable),
                ("المخزون",                   bs.inventory),
                ("أصول متداولة أخرى",        bs.other_current_assets),
                ("إجمالي الأصول المتداولة",  bs.current_assets),
            ]),
            ("الأصول الثابتة والطويلة الأجل", [
                ("الأصول الثابتة (الإجمالي)", bs.fixed_assets),
                ("(-) مجمع الاستهلاك",        -bs.accumulated_depreciation),
                ("صافي الأصول الثابتة",       bs.net_fixed_assets),
                ("أصول طويلة الأجل أخرى",    bs.other_long_term_assets),
                ("إجمالي الأصول",             bs.total_assets),
            ]),
            ("الالتزامات المتداولة", [
                ("الذمم الدائنة",              bs.accounts_payable),
                ("ديون قصيرة الأجل",           bs.short_term_debt),
                ("التزامات متداولة أخرى",       bs.other_current_liabilities),
                ("إجمالي الالتزامات المتداولة", bs.current_liabilities),
            ]),
            ("الالتزامات طويلة الأجل وحقوق الملكية", [
                ("ديون طويلة الأجل",           bs.long_term_debt),
                ("التزامات طويلة الأجل أخرى",  bs.other_long_term_liabilities),
                ("إجمالي الالتزامات",          bs.total_liabilities),
                ("رأس المال المدفوع",          bs.paid_in_capital),
                ("الأرباح المحتجزة",           bs.retained_earnings),
                ("إجمالي حقوق الملكية",        bs.total_equity),
                ("إجمالي الالتزامات + حقوق الملكية", bs.total_liabilities_equity),
            ]),
        ]

        bs_data = [["البند", f"القيمة ({currency})"]]
        for sec_title, items in bs_sections:
            bs_data.append([Paragraph(f"── {sec_title} ──", ParagraphStyle(
                "sh", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=13)), ""])
            for label, val in items:
                is_total = "إجمالي" in label or "صافي" in label
                fn = arabic_bold if is_total else arabic_font
                c  = GOLD if "إجمالي الأصول" in label or "إجمالي الالتزامات + حقوق" in label else (ACCENT if is_total else LIGHT)
                bs_data.append([
                    Paragraph(f"  {label}", ParagraphStyle("r", fontName=fn, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13)),
                    Paragraph(f"{val:,.0f}", ParagraphStyle("v", fontName=fn, fontSize=9, textColor=c, alignment=TA_LEFT, leading=13)),
                ])

        bs_table = Table(bs_data, colWidths=[W*0.65, W*0.35])
        bs_table.setStyle(_table_style_base(ACCENT))
        story.append(bs_table)

        balanced = abs(bs.total_assets - bs.total_liabilities_equity) < 1
        status_text = "✅ الميزانية متوازنة" if balanced else f"❌ فرق: {bs.total_assets - bs.total_liabilities_equity:,.0f}"
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(status_text, ParagraphStyle(
            "bal", fontName=arabic_bold, fontSize=12,
            textColor=SUCCESS if balanced else DANGER,
            alignment=TA_CENTER, leading=18)))
        story.append(Spacer(1, 0.35*cm))

    # ─────────────────────────────────────────────
    #  4. التدفقات النقدية
    # ─────────────────────────────────────────────
    if cf:
        story.append(Paragraph("4. قائمة التدفقات النقدية — Cash Flow Statement", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=TEAL))
        story.append(Spacer(1, 0.3*cm))

        cf_sections = [
            ("أنشطة التشغيل", [
                ("صافي الدخل",                  cf.net_income),
                ("الاستهلاك والإطفاء",          cf.depreciation_add_back),
                ("التغير في الذمم المدينة",      cf.change_in_receivables),
                ("التغير في المخزون",            cf.change_in_inventory),
                ("التغير في الذمم الدائنة",      cf.change_in_payables),
                ("تعديلات أخرى",                cf.other_operating),
                ("صافي التدفق التشغيلي",        cf.operating_cash_flow),
            ]),
            ("أنشطة الاستثمار", [
                ("النفقات الرأسمالية CAPEX",    cf.capex),
                ("عائدات بيع أصول",             cf.asset_sales),
                ("استثمارات أخرى",              cf.other_investing),
                ("صافي التدفق الاستثماري",      cf.investing_cash_flow),
            ]),
            ("أنشطة التمويل", [
                ("اقتراض جديد",                 cf.debt_issued),
                ("سداد ديون",                   cf.debt_repaid),
                ("توزيعات أرباح",               cf.dividends_paid),
                ("إصدار أسهم",                  cf.equity_issued),
                ("صافي التدفق التمويلي",        cf.financing_cash_flow),
            ]),
            ("ملخص النقد", [
                ("رصيد النقد أول الفترة",       cf.beginning_cash),
                ("صافي التغير في النقد",        cf.net_change_in_cash),
                ("التدفق النقدي الحر FCF",      cf.free_cash_flow),
                ("رصيد النقد آخر الفترة",       cf.ending_cash),
            ]),
        ]

        cf_data = [["البند", f"القيمة ({currency})"]]
        for sec_title, items in cf_sections:
            cf_data.append([Paragraph(f"── {sec_title} ──", ParagraphStyle(
                "sh", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=13)), ""])
            for label, val in items:
                is_total = "صافي" in label or "رصيد" in label or "حر" in label
                fn = arabic_bold if is_total else arabic_font
                c  = TEAL if is_total else (SUCCESS if val >= 0 else DANGER)
                cf_data.append([
                    Paragraph(f"  {label}", ParagraphStyle("r", fontName=fn, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13)),
                    Paragraph(f"{val:,.0f}", ParagraphStyle("v", fontName=fn, fontSize=9, textColor=c, alignment=TA_LEFT, leading=13)),
                ])

        cf_table = Table(cf_data, colWidths=[W*0.65, W*0.35])
        cf_table.setStyle(_table_style_base(TEAL))
        story.append(cf_table)
        story.append(Spacer(1, 0.35*cm))

    # Cross-statement integrity: ending cash must reconcile to balance-sheet cash.
    cash_gap = (bs.cash - cf.ending_cash) if (bs and cf) else 0
    cash_tolerance = max(1.0, abs(bs.cash) * 0.0001) if bs else 1.0
    cash_reconciled = (not cf) or abs(cash_gap) <= cash_tolerance
    ni_gap = (cf.net_income - inc.net_income) if (inc and cf) else 0
    ni_tolerance = max(1.0, abs(inc.net_income) * 0.0001) if inc else 1.0
    ni_reconciled = (not cf) or abs(ni_gap) <= ni_tolerance
    integrity_ok = bool(bs and bs.is_balanced and cash_reconciled and ni_reconciled)

    if bs and cf and not cash_reconciled:
        story.append(Paragraph("تنبيه سلامة القوائم — مطابقة النقد غير مجتازة", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=DANGER))
        cash_check = [
            ["فحص المطابقة", "القيمة"],
            ["النقد وما في حكمه — الميزانية", f"{bs.cash:,.0f} {currency}"],
            ["رصيد النقد آخر الفترة — التدفقات", f"{cf.ending_cash:,.0f} {currency}"],
            ["فرق مطابقة النقد", f"{cash_gap:,.0f} {currency}"],
            ["الحالة", "غير مجتاز — التقييم النهائي محجوب"],
        ]
        cash_table = Table(cash_check, colWidths=[W*0.62, W*0.38])
        cash_table.setStyle(_table_style_base(DANGER))
        story.append(cash_table)
        story.append(Spacer(1, 0.35*cm))

    # ─────────────────────────────────────────────
    #  5. النسب المالية
    # ─────────────────────────────────────────────
    if inc and bs:
        from core.financial_engine import FinancialRatios
        ratios = FinancialRatios(inc, bs, cf, getattr(app, 'sector', ''))
        all_ratios = ratios.get_all_ratios()
        interpretations = ratios.get_interpretation()
        if not bs.is_balanced:
            # Do not publish balance-dependent KPIs from a failed accounting equation.
            profit = all_ratios.get("نسب الربحية", {})
            all_ratios = {"مؤشرات قائمة الدخل المستقلة": {
                k: v for k, v in profit.items()
                if k in {"هامش المبيعات الإجمالي %", "هامش EBITDA %", "هامش التشغيل %", "هامش صافي الدخل %"}
            }}
            interpretations = [x for x in interpretations if x[1] in {"هامش الربح"}]

        story.append(Paragraph("5. النسب المالية — Financial Ratios (Advanced Financial Analysis Framework)", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=PURPLE))
        story.append(Spacer(1, 0.3*cm))

        benchmarks = {
            "نسبة التداول":                    ">= 2.0",
            "نسبة السيولة السريعة":            ">= 1.0",
            "هامش صافي الدخل %":               ">= 10%",
            "العائد على حقوق الملكية ROE %":   ">= 15%",
            "نسبة الدين إلى الأصول":           "< 0.50",
            "نسبة تغطية الفائدة":              ">= 3.0x",
            "معدل دوران الأصول":               ">= 0.5",
        }

        ratios_data = [["الفئة", "النسبة", "القيمة", "المعيار"]]
        for category, items in all_ratios.items():
            for name, value in items.items():
                bench = benchmarks.get(name, "—")
                ratios_data.append([
                    Paragraph(category, ParagraphStyle("c", fontName=arabic_font, fontSize=8, textColor=DIM, alignment=TA_CENTER, leading=12)),
                    Paragraph(_pdf_kpi_label(name), ParagraphStyle("n", fontName=arabic_font, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13)),
                    Paragraph(f"{value:.2f}" if isinstance(value, (int, float)) else str(value), ParagraphStyle("v", fontName=arabic_bold, fontSize=9, textColor=ACCENT, alignment=TA_CENTER, leading=13)),
                    Paragraph(bench, ParagraphStyle("b", fontName=arabic_font, fontSize=8, textColor=DIM, alignment=TA_CENTER, leading=12)),
                ])

        ratios_table = Table(ratios_data, colWidths=[W*0.18, W*0.49, W*0.14, W*0.19], repeatRows=1)
        ratios_table.setStyle(_table_style_base(PURPLE))
        ratios_table.setStyle(TableStyle([
            ("FONTSIZE", (0,0), (-1,-1), 7.4),
            ("TOPPADDING", (0,0), (-1,-1), 2.2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2.2),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(ratios_table)
        story.append(Spacer(1, 0.28*cm))

        # Executive report: keep only the four highest-value readings instead of
        # spilling a verbose interpretation list onto a mostly empty page.
        story.append(Paragraph("القراءة التنفيذية للمؤشرات", ParagraphStyle(
            "ratio_readout", fontName=arabic_bold, fontSize=10.5, textColor=GOLD, alignment=TA_RIGHT, leading=15, spaceAfter=3)))
        key_interpretations = interpretations[:4]
        readout_data = []
        for icon, category, note in key_interpretations:
            c = SUCCESS if "✅" in icon else (WARNING if "⚠️" in icon else (DANGER if "❌" in icon else ACCENT))
            readout_data.append([
                Paragraph(category, ParagraphStyle("rc", fontName=arabic_bold, fontSize=7.5, textColor=c, alignment=TA_RIGHT, leading=11)),
                Paragraph(note, ParagraphStyle("rn", fontName=arabic_font, fontSize=7.5, textColor=INK, alignment=TA_RIGHT, leading=11)),
            ])
        if readout_data:
            readout_table = Table(readout_data, colWidths=[W*0.22, W*0.78])
            readout_table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), white),
                ("BOX", (0,0), (-1,-1), 0.5, BORDER),
                ("INNERGRID", (0,0), (-1,-1), 0.35, BORDER),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ]))
            story.append(readout_table)
        story.append(Spacer(1, 0.25*cm))

    # ─────────────────────────────────────────────
    #  6. التحليلات المتقدمة
    # ─────────────────────────────────────────────
    if inc and bs and integrity_ok:
        story.append(PageBreak())
        story.append(Paragraph("6. تحليلات القيمة والكفاءة المتقدمة", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=WARNING))
        story.append(Spacer(1, 0.3*cm))

        # DuPont
        story.append(Paragraph("تحليل دوبونت لتفكيك العائد على حقوق الملكية", ParagraphStyle(
            "sub", fontName=arabic_bold, fontSize=11, textColor=GOLD, alignment=TA_RIGHT, leading=16, spaceAfter=4)))
        dupont = ratios.dupont_analysis()
        dp_data = [["المؤشر", "القيمة"]]
        for name, val in dupont.items():
            dp_data.append([
                Paragraph(_pdf_kpi_label(name).replace("ROE", "العائد على حقوق الملكية").replace("EBIT", "الربح التشغيلي"), ParagraphStyle("n", fontName=arabic_font, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13)),
                Paragraph(f"{val:.4f}" if isinstance(val, (int, float)) else str(val), ParagraphStyle("v", fontName=arabic_bold, fontSize=9, textColor=ACCENT, alignment=TA_CENTER, leading=13)),
            ])
        dp_table = Table(dp_data, colWidths=[W*0.7, W*0.3])
        dp_table.setStyle(_table_style_base(WARNING))
        story.append(dp_table)
        story.append(Spacer(1, 0.3*cm))

        # EVA
        story.append(Paragraph("القيمة الاقتصادية المضافة", ParagraphStyle(
            "sub", fontName=arabic_bold, fontSize=11, textColor=GOLD, alignment=TA_RIGHT, leading=16, spaceAfter=4)))
        story.append(Paragraph("EVA  |  WACC = 10%", ParagraphStyle("sub_en_eva", fontName="Helvetica-Bold", fontSize=8, textColor=DIM, alignment=TA_RIGHT, leading=11, spaceAfter=3)))
        eva = ratios.economic_value_added(0.10)
        eva_data = [["المؤشر", "القيمة"]]
        for name, val in eva.items():
            if name == "_color":
                continue
            c = SUCCESS if (isinstance(val, str) and "تخلق" in val) or (isinstance(val, (int, float)) and val > 0) else DANGER
            if name == "أساس رأس المال المستثمر":
                value_flowable = RLParagraph("Equity + Interest-bearing debt - Cash", ParagraphStyle("eva_formula", fontName="Helvetica-Bold", fontSize=7.2, textColor=LIGHT, alignment=TA_CENTER, leading=10, wordWrap="LTR"))
            else:
                value_flowable = Paragraph(str(val) if isinstance(val, str) else f"{val:,.2f}", ParagraphStyle("v", fontName=arabic_bold, fontSize=9, textColor=c, alignment=TA_CENTER, leading=13))
            eva_data.append([
                Paragraph(name, ParagraphStyle("n", fontName=arabic_font, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13)),
                value_flowable,
            ])
        eva_table = Table(eva_data, colWidths=[W*0.7, W*0.3])
        eva_table.setStyle(_table_style_base(WARNING))
        story.append(eva_table)
        story.append(Spacer(1, 0.3*cm))

        # Altman Z-Score
        story.append(Paragraph("مؤشر ألتمان للفحص الكمي للتعثر المالي", ParagraphStyle(
            "sub", fontName=arabic_bold, fontSize=11, textColor=GOLD, alignment=TA_RIGHT, leading=16, spaceAfter=4)))
        z_data = ratios.altman_z_score()
        z_is_manufacturing = z_data.get("_model_code") == "ALTMAN_Z_PRIME_PRIVATE_MANUFACTURING"
        z_model_en = ("Altman Z-prime | Private manufacturing model"
                      if z_is_manufacturing else
                      "Altman Z-double-prime | Private non-manufacturing model")
        story.append(RLParagraph(z_model_en, ParagraphStyle("sub_en_z", fontName="Helvetica-Bold", fontSize=8, textColor=DIM, alignment=TA_LEFT, leading=11, spaceAfter=3, wordWrap="LTR")))
        color_map = {"green": SUCCESS, "orange": WARNING, "red": DANGER}
        z_color = color_map.get(z_data.get("_color", "green"), SUCCESS)
        z_val = z_data.get("Z-Score", 0)
        story.append(Paragraph(
            f"النتيجة: {z_val:.3f} — {z_data.get('المنطقة', '')} — {z_data.get('تقييم المخاطر', '')}",
            ParagraphStyle("zs", fontName=arabic_bold, fontSize=12, textColor=z_color, alignment=TA_CENTER, leading=18)))
        z_label = ParagraphStyle("z_label", fontName=arabic_bold, fontSize=8.5, textColor=LIGHT, alignment=TA_RIGHT, leading=12)
        z_ar = ParagraphStyle("z_ar", fontName=arabic_font, fontSize=8.5, textColor=LIGHT, alignment=TA_RIGHT, leading=12)
        z_en = ParagraphStyle("z_en", fontName="Helvetica-Bold", fontSize=8, textColor=LIGHT, alignment=TA_CENTER, leading=12)
        if z_is_manufacturing:
            z_method = [
                [Paragraph("النموذج", z_label), Paragraph("الشركات الصناعية الخاصة", z_ar)],
                [Paragraph("المعادلة", z_label), Paragraph("Z' = 0.717 X1 + 0.847 X2 + 3.107 X3 + 0.420 X4 + 0.998 X5", z_en)],
                [Paragraph("المنطقة الآمنة", z_label), Paragraph("Z' > 2.90", z_en)],
                [Paragraph("المنطقة الرمادية", z_label), Paragraph("1.23 <= Z' <= 2.90", z_en)],
                [Paragraph("منطقة التعثر", z_label), Paragraph("Z' < 1.23", z_en)],
                [Paragraph("النطاق", z_label), Paragraph(z_data.get("ملاحظة منهجية", ""), z_ar)],
            ]
        else:
            z_method = [
                [Paragraph("النموذج", z_label), Paragraph("الشركات الخاصة غير الصناعية", z_ar)],
                [Paragraph("المعادلة", z_label), Paragraph("Z'' = 6.56 X1 + 3.26 X2 + 6.72 X3 + 1.05 X4", z_en)],
                [Paragraph("المنطقة الآمنة", z_label), Paragraph("Z'' > 2.60", z_en)],
                [Paragraph("المنطقة الرمادية", z_label), Paragraph("1.10 <= Z'' <= 2.60", z_en)],
                [Paragraph("منطقة التعثر", z_label), Paragraph("Z'' < 1.10", z_en)],
                [Paragraph("النطاق", z_label), Paragraph(z_data.get("ملاحظة منهجية", ""), z_ar)],
            ]
        zt = Table(z_method, colWidths=[W*0.24, W*0.76])
        zt.setStyle(_table_style_base(z_color))
        story.append(Spacer(1, 0.15*cm)); story.append(zt)
        story.append(Spacer(1, 0.35*cm))

    if inc and bs and not integrity_ok:
        story.append(Paragraph("6. التحليلات المتقدمة — محجوبة مؤقتًا", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=WARNING))
        story.append(Spacer(1, 0.25*cm))
        balance_gap = bs.total_assets - bs.total_liabilities_equity
        failed_checks = []
        if not bs.is_balanced: failed_checks.append("مطابقة الميزانية")
        if not cash_reconciled: failed_checks.append("مطابقة النقد بين القوائم")
        if not ni_reconciled: failed_checks.append("مطابقة صافي الدخل بين قائمتي الدخل والتدفقات")
        integrity_reason = " و".join(failed_checks)
        gov_data = [
            [Paragraph("سبب الحجب", ParagraphStyle("gov_k", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph(f"عدم اجتياز {integrity_reason}", ParagraphStyle("gov_v", fontName=arabic_bold, fontSize=9, textColor=WARNING, alignment=TA_RIGHT, leading=14))],
            [Paragraph("فرق الميزانية", ParagraphStyle("gov_k2", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph(f"{balance_gap:,.0f} {currency}", ParagraphStyle("gov_num", fontName=arabic_bold, fontSize=9, textColor=DANGER, alignment=TA_CENTER, leading=14))],
            [Paragraph("فرق مطابقة النقد", ParagraphStyle("gov_k_cash", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph(f"{cash_gap:,.0f} {currency}" if cf else "—", ParagraphStyle("gov_cash", fontName=arabic_bold, fontSize=9, textColor=DANGER if cf and not cash_reconciled else SUCCESS, alignment=TA_CENTER, leading=14))],
            [Paragraph("صافي دخل قائمة الدخل", ParagraphStyle("gov_k_ni1", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph(f"{inc.net_income:,.0f} {currency}", ParagraphStyle("gov_ni1", fontName=arabic_bold, fontSize=9, textColor=LIGHT, alignment=TA_CENTER, leading=14))],
            [Paragraph("صافي الدخل المستخدم في التدفقات", ParagraphStyle("gov_k_ni2", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph(f"{cf.net_income:,.0f} {currency}" if cf else "—", ParagraphStyle("gov_ni2", fontName=arabic_bold, fontSize=9, textColor=LIGHT, alignment=TA_CENTER, leading=14))],
            [Paragraph("فرق مطابقة صافي الدخل", ParagraphStyle("gov_k_ni3", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph(f"{ni_gap:,.0f} {currency}" if cf else "—", ParagraphStyle("gov_ni3", fontName=arabic_bold, fontSize=9, textColor=DANGER if cf and not ni_reconciled else SUCCESS, alignment=TA_CENTER, leading=14))],
            [Paragraph("المؤشرات المحجوبة", ParagraphStyle("gov_k3", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph("DuPont · EVA · Altman Z-Score", ParagraphStyle("gov_en", fontName="Helvetica-Bold", fontSize=8, textColor=LIGHT, alignment=TA_CENTER, leading=14))],
            [Paragraph("إعادة الإتاحة", ParagraphStyle("gov_k4", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=14)), Paragraph("تلقائيًا بعد تصحيح البيانات واجتياز المطابقة", ParagraphStyle("gov_v2", fontName=arabic_font, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=14))],
        ]
        gov_table = Table(gov_data, colWidths=[W*0.28, W*0.72])
        gov_table.setStyle(_table_style_base(WARNING))
        story.append(gov_table)
        story.append(Spacer(1, 0.35*cm))

    # ─────────────────────────────────────────────
    #  7. التقييم المالي الشامل
    # ─────────────────────────────────────────────
    if inc and bs:
        scorecard = FinancialScorecard(inc, bs, cf).calculate()
        total_score = scorecard["التقييم_الإجمالي"]
        grade       = scorecard["التصنيف"]
        desc        = scorecard["الوصف"]
        provisional = (scorecard.get("حالة_التقييم") == "PROVISIONAL") or (not integrity_ok)
        if not integrity_ok:
            desc = "سلامة القوائم تحتاج مراجعة"
        score_color = WARNING if provisional else (SUCCESS if total_score >= 80 else (WARNING if total_score >= 60 else DANGER))

        story.append(PageBreak())
        story.append(Paragraph("7. التقييم المالي الشامل", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=score_color))
        story.append(Spacer(1, 0.3*cm))
        story.append(_score_banner(total_score, grade, desc, provisional, score_color, arabic_font, arabic_bold, W))
        story.append(_score_methodology_table(scorecard, arabic_font, arabic_bold, W))
        if not provisional:
            story.append(Paragraph(
                f"ثقة القراءة: {scorecard.get('ثقة_القراءة', '—')} | عدد الاختبارات الكمية: {scorecard.get('عدد_الاختبارات', 0)}",
                ParagraphStyle("score_conf", fontName=arabic_bold, fontSize=9, textColor=INK, alignment=TA_CENTER, leading=14)))
        story.append(Spacer(1, 0.3*cm))

        if provisional:
            story.append(Paragraph(
                "لا تُعرض درجة إجمالية أو درجات محاور نهائية قبل اجتياز اختبارات سلامة القوائم. تبقى مؤشرات قائمة الدخل المستقلة متاحة للقراءة المبدئية، وتُقرأ التدفقات بوصفها محسوبة إلى حين مطابقة النقد الختامي.",
                ParagraphStyle("score_gov", fontName=arabic_bold, fontSize=10, textColor=WARNING, alignment=TA_CENTER, leading=17)))
            sc_data = [["الفحص", "النتيجة"]]
            sc_data.append(["مطابقة الميزانية", "مجتاز" if bs.is_balanced else "غير مجتاز — محجوب"])
            if cf:
                sc_data.append(["مطابقة النقد بين القوائم", "مجتاز" if cash_reconciled else "غير مجتاز — محجوب"])
                sc_data.append(["مطابقة صافي الدخل بين الدخل والتدفقات", "مجتاز" if ni_reconciled else "غير مجتاز — محجوب"])
        else:
            sc_data = [["المحور", "الدرجة", "من", "النسبة"]]
        for axis, data in ([] if provisional else scorecard["المحاور"].items()):
            s = data["الدرجة"]; m = data["من"]
            pct = s / m
            c = SUCCESS if pct >= 0.75 else (WARNING if pct >= 0.5 else DANGER)
            sc_data.append([
                Paragraph(axis, ParagraphStyle("a", fontName=arabic_font, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=13)),
                Paragraph(str(s), ParagraphStyle("s", fontName=arabic_bold, fontSize=9, textColor=c, alignment=TA_CENTER, leading=13)),
                Paragraph(str(m), ParagraphStyle("m", fontName=arabic_font, fontSize=9, textColor=DIM, alignment=TA_CENTER, leading=13)),
                Paragraph(f"{pct:.0%}", ParagraphStyle("p", fontName=arabic_bold, fontSize=9, textColor=c, alignment=TA_CENTER, leading=13)),
            ])

        sc_table = Table(sc_data, colWidths=([W*0.5, W*0.5] if provisional else [W*0.5, W*0.15, W*0.15, W*0.2]))
        sc_table.setStyle(_table_style_base(score_color))
        story.append(sc_table)
        if not provisional:
            story.append(Spacer(1, 0.22*cm))
            story.append(Paragraph("أساس احتساب الدرجة", ParagraphStyle(
                "score_basis", fontName=arabic_bold, fontSize=10, textColor=GOLD, alignment=TA_RIGHT, leading=15)))
            basis_data = [["المحور", "الاختبار", "النتيجة"]]
            for axis, axis_data in scorecard["المحاور"].items():
                for test_name, test_score, test_max, note in axis_data.get("التفاصيل", []):
                    basis_data.append([
                        Paragraph(axis, ParagraphStyle("ba", fontName=arabic_font, fontSize=7.5, textColor=DIM, alignment=TA_RIGHT, leading=11)),
                        Paragraph(_pdf_kpi_label(test_name), ParagraphStyle("bt", fontName=arabic_font, fontSize=7.5, textColor=LIGHT, alignment=TA_RIGHT, leading=11)),
                        RLParagraph(f"{test_score} / {test_max}", ParagraphStyle("bs", fontName="Helvetica-Bold", fontSize=7.5, textColor=ACCENT, alignment=TA_CENTER, leading=11)),
                    ])
            basis_table = Table(basis_data, colWidths=[W*0.30, W*0.52, W*0.18], repeatRows=1)
            basis_table.setStyle(_table_style_base(score_color))
            story.append(basis_table)
        story.append(Spacer(1, 0.35*cm))

    # ─────────────────────────────────────────────
    #  8. تحليل المخاطر
    # ─────────────────────────────────────────────
    if inc and bs and integrity_ok:
        story.append(PageBreak())
        from core.financial_engine import RiskAnalysis
        risk_engine = RiskAnalysis(inc, bs, cf, sector)
        risks   = risk_engine.get_all_risks()
        overall = risk_engine.overall_risk_level()
        overall_color = {"منخفض": SUCCESS, "متوسط": WARNING, "مرتفع": DANGER}[overall]

        story.append(Paragraph("8. تحليل المخاطر المالية", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=overall_color))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f"مستوى المخاطر الإجمالي: {overall}", ParagraphStyle(
            "ov", fontName=arabic_bold, fontSize=12, textColor=overall_color, alignment=TA_CENTER, leading=18)))
        story.append(Spacer(1, 0.2*cm))

        risk_data = [["المخاطرة", "المستوى", "الدرجة", "الوصف"]]
        for risk in risks:
            level = risk["المستوى"]
            c = {"منخفض": SUCCESS, "متوسط": WARNING, "مرتفع": DANGER}[level]
            risk_data.append([
                Paragraph(str(risk["المخاطرة"]), ParagraphStyle("r", fontName=arabic_bold, fontSize=9, textColor=c, alignment=TA_RIGHT, leading=13)),
                Paragraph(level, ParagraphStyle("l", fontName=arabic_font, fontSize=9, textColor=c, alignment=TA_CENTER, leading=13)),
                Paragraph(str(risk["الدرجة"]), ParagraphStyle("d", fontName=arabic_bold, fontSize=9, textColor=c, alignment=TA_CENTER, leading=13)),
                Paragraph(risk["الوصف"], ParagraphStyle("desc", fontName=arabic_font, fontSize=8, textColor=LIGHT, alignment=TA_RIGHT, leading=12)),
            ])

        risk_table = Table(risk_data, colWidths=[W*0.22, W*0.12, W*0.1, W*0.56])
        risk_table.setStyle(_table_style_base(overall_color))
        story.append(risk_table)
        story.append(Spacer(1, 0.35*cm))

    # ─────────────────────────────────────────────
    #  9. الأولويات والتوصيات التنفيذية
    #  PDF presentation layer only: preserve engine output and enrich sparse pages
    #  with neutral monitoring actions derived from already-calculated ratios.
    # ─────────────────────────────────────────────
    if inc and bs and integrity_ok:
        from core.financial_engine import SmartRecommendations
        smart = SmartRecommendations(inc, bs, cf)
        recs  = list(smart.get_recommendations())

        # Keep the recommendation engine untouched. If its exception-based output
        # is sparse, complete the executive page with non-warning monitoring actions.
        if len(recs) < 3:
            ratios = smart.ratios
            monitoring = [
                (3, "السيولة", "ضبط حد السيولة التشغيلي",
                 f"نسبة التداول الحالية {ratios.current_ratio():.2f}x؛ يُوصى بتثبيت حد داخلي للسيولة ومراجعته شهرياً مقابل الالتزامات قصيرة الأجل.",
                 "حماية هامش الأمان السيولي واستباق ضغوط رأس المال العامل"),
                (3, "رأس المال العامل", "مراقبة دورة التحصيل",
                 f"أيام التحصيل الحالية {ratios.days_receivables():.0f} يوم؛ يُوصى بمتابعة اتجاه المؤشر شهرياً وربطه بأعمار الذمم وحدود الائتمان.",
                 "رفع انضباط التحصيل وتحسين قابلية التنبؤ بالتدفقات"),
            ]
            if cf:
                monitoring.append(
                    (3, "التدفقات النقدية", "حماية جودة التدفق النقدي الحر",
                     f"التدفق النقدي الحر الحالي {cf.free_cash_flow:,.0f}؛ يُوصى بمراجعته دورياً مقابل النفقات الرأسمالية وخدمة الدين.",
                     "دعم استدامة التمويل الذاتي وكفاءة تخصيص النقد")
                )
            else:
                monitoring.append(
                    (3, "المديونية", "مراقبة قدرة خدمة الدين",
                     f"تغطية الفائدة الحالية {ratios.interest_coverage():.2f}x؛ يُوصى بتتبعها دورياً مع أي تمويل جديد.",
                     "الحفاظ على مرونة التمويل وقدرة خدمة الالتزامات")
                )

            existing_titles = {r[2] for r in recs}
            for item in monitoring:
                if item[2] not in existing_titles and len(recs) < 3:
                    recs.append(item)
                    existing_titles.add(item[2])

        recs.sort(key=lambda r: r[0])

        story.append(Paragraph("9. الأولويات والتوصيات التنفيذية", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=GOLD))
        story.append(Spacer(1, 0.22*cm))

        urgent_count = sum(1 for r in recs if r[0] == 1)
        important_count = sum(1 for r in recs if r[0] == 2)
        improve_count = sum(1 for r in recs if r[0] == 3)

        brief_style = ParagraphStyle(
            "rec_brief", fontName=arabic_font, fontSize=8.5,
            textColor=LIGHT, alignment=TA_RIGHT, leading=13
        )
        brief_value_style = ParagraphStyle(
            "rec_brief_value", fontName=arabic_bold, fontSize=14,
            textColor=GOLD, alignment=TA_CENTER, leading=17
        )
        brief_label_style = ParagraphStyle(
            "rec_brief_label", fontName=arabic_font, fontSize=7.5,
            textColor=LIGHT, alignment=TA_CENTER, leading=11
        )

        brief_data = [[
            Paragraph(f"<b>{len(recs)}</b><br/>إجراء تنفيذي", brief_value_style),
            Paragraph(f"<b>{urgent_count}</b><br/>أولوية عاجلة", brief_value_style),
            Paragraph(f"<b>{important_count}</b><br/>أولوية مهمة", brief_value_style),
            Paragraph(f"<b>{improve_count}</b><br/>تحسين ومراقبة", brief_value_style),
        ]]
        brief_table = Table(brief_data, colWidths=[W*0.25]*4, hAlign="CENTER")
        brief_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CARD),
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(brief_table)
        story.append(Spacer(1, 0.18*cm))
        story.append(Paragraph(
            "مصفوفة الإجراءات أدناه ترتب الأولويات حسب الحاجة التنفيذية. بنود «تحسين ومراقبة» تمثل ضوابط متابعة دورية وليست مؤشرات تعثر مستقلة.",
            brief_style
        ))
        story.append(Spacer(1, 0.18*cm))

        priority_labels = {1: "عاجل", 2: "مهم", 3: "تحسين"}
        priority_colors = {1: DANGER, 2: WARNING, 3: SUCCESS}
        rec_data = [["الأولوية", "المجال", "الإجراء التنفيذي", "الأثر المتوقع"]]
        for priority, category, title, rec, impact in recs:
            p_label = priority_labels.get(priority, "متابعة")
            c = priority_colors.get(priority, ACCENT)
            rec_data.append([
                Paragraph(p_label, ParagraphStyle("p", fontName=arabic_bold, fontSize=8.5, textColor=c, alignment=TA_CENTER, leading=13)),
                Paragraph(category, ParagraphStyle("cat", fontName=arabic_bold, fontSize=8.5, textColor=GOLD, alignment=TA_RIGHT, leading=13)),
                Paragraph(
                    f"<b>{title}</b><br/><font size='7.8'>{rec}</font>",
                    ParagraphStyle(
                        "r", fontName=arabic_font, fontSize=8.2,
                        textColor=LIGHT, alignment=TA_RIGHT,
                        leading=12.2, splitLongWords=False,
                    ),
                ),
                Paragraph(
                    impact,
                    ParagraphStyle(
                        "i", fontName=arabic_font, fontSize=8.0,
                        textColor=TEAL, alignment=TA_RIGHT,
                        leading=12.2, splitLongWords=False,
                    ),
                ),
            ])

        rec_table = Table(
            rec_data,
            colWidths=[W*0.09, W*0.15, W*0.54, W*0.22],
            repeatRows=1,
            hAlign="CENTER",
        )
        rec_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), GOLD),
            ("TEXTCOLOR",     (0, 0), (-1, 0), DARK),
            ("FONTNAME",      (0, 0), (-1, 0), arabic_bold),
            ("FONTSIZE",      (0, 0), (-1, 0), 9),
            ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [MEDIUM, CARD]),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING",    (0, 0), (-1, 0), 7),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
            ("TOPPADDING",    (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 0.35*cm))


    if inc and bs and not integrity_ok:
        story.append(Paragraph("8. تحليل المخاطر المالية — محجوب مؤقتًا", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=WARNING))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph("لم يُصدر مستوى مخاطر إجمالي لعدم اجتياز اختبارات سلامة القوائم. تبقى مؤشرات قائمة الدخل المستقلة متاحة، وتظل نتائج التدفقات قراءة محسوبة إلى حين مطابقة رصيد النقد الختامي مع الميزانية.", ParagraphStyle("risk_gov", fontName=arabic_bold, fontSize=10, textColor=WARNING, alignment=TA_RIGHT, leading=17)))
        story.append(Spacer(1, 0.35*cm))
        story.append(Paragraph("9. الأولويات والتوصيات التنفيذية — قراءة محكومة", styles["section"]))
        story.append(HRFlowable(width=W, thickness=1, color=GOLD))
        story.append(Spacer(1, 0.2*cm))
        governed_recs = []
        if not bs.is_balanced:
            governed_recs.append([str(len(governed_recs)+1), "سلامة الميزانية", "تصحيح فرق الميزانية وإعادة مطابقة الأصول مع الالتزامات وحقوق الملكية"])
        if cf and not cash_reconciled:
            governed_recs.append([str(len(governed_recs)+1), "مطابقة النقد", "مطابقة رصيد النقد الختامي في قائمة التدفقات مع بند النقد وما في حكمه في الميزانية"])
        governed_recs.append([str(len(governed_recs)+1), "إعادة التحليل", "إعادة تشغيل التحليل بعد اجتياز اختبارات السلامة لإتاحة التقييم والمؤشرات المحجوبة"])
        gov_rec_data = [["الأولوية", "المجال", "الإجراء التنفيذي"]]
        for priority, area, action in governed_recs:
            gov_rec_data.append([Paragraph(priority, ParagraphStyle("gp", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD, alignment=TA_CENTER, leading=13)), Paragraph(area, ParagraphStyle("ga", fontName=arabic_bold, fontSize=9, textColor=GOLD, alignment=TA_RIGHT, leading=13)), Paragraph(action, ParagraphStyle("gx", fontName=arabic_font, fontSize=9, textColor=LIGHT, alignment=TA_RIGHT, leading=14))])
        gov_rec_table = Table(gov_rec_data, colWidths=[W*0.12, W*0.23, W*0.65])
        gov_rec_table.setStyle(_table_style_base(GOLD))
        story.append(gov_rec_table)
        story.append(Spacer(1, 0.5*cm))


    # ─────────────────────────────────────────────
    #  صفحة ختامية — هوية FYQ وحقوق الملكية
    # ─────────────────────────────────────────────
    story.append(PageBreak())
    closing_brand = ParagraphStyle(
        "closing_brand", fontName="Helvetica-Bold", fontSize=36,
        textColor=DARK, alignment=TA_CENTER, leading=42,
    )
    closing_title = ParagraphStyle(
        "closing_title", fontName="Helvetica-Bold", fontSize=14,
        textColor=ACCENT, alignment=TA_CENTER, leading=20,
    )
    closing_copy = ParagraphStyle(
        "closing_copy", fontName=arabic_font, fontSize=11,
        textColor=INK, alignment=TA_CENTER, leading=19,
    )
    closing_meta = ParagraphStyle(
        "closing_meta", fontName="Helvetica", fontSize=10,
        textColor=HexColor("#C8D6E5"), alignment=TA_CENTER, leading=17,
    )
    closing_name = ParagraphStyle(
        "closing_name", fontName="Helvetica-Bold", fontSize=13,
        textColor=white, alignment=TA_CENTER, leading=18,
    )

    story.append(Spacer(1, 4.3 * cm))
    story.append(Paragraph("FYQ", closing_brand))
    story.append(Spacer(1, 0.16 * cm))
    story.append(Paragraph("FINANCIAL INTELLIGENCE PLATFORM", closing_title))
    story.append(Spacer(1, 0.62 * cm))
    story.append(HRFlowable(width=W * 0.56, thickness=1.2, color=GOLD, hAlign="CENTER"))
    story.append(Spacer(1, 0.62 * cm))
    story.append(Paragraph("منصة الذكاء المالي لاتخاذ قرارات أوضح بثقة أعلى.", closing_copy))
    story.append(Spacer(1, 1.05 * cm))

    closing_table = Table([
        [Paragraph("DEVELOPED BY", closing_meta)],
        [Paragraph("SANAD ALANZI", closing_name)],
        [Paragraph("CONTACT", closing_meta)],
        [Paragraph("0579599909", closing_name)],
        [Paragraph("© All Rights Reserved", closing_meta)],
    ], colWidths=[W * 0.58], hAlign="CENTER")
    closing_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK),
        ("BOX", (0, 0), (-1, -1), 0.8, ACCENT),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, HexColor("#2B4057")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(closing_table)

    # ─────────────────────────────────────────────
    #  البناء النهائي — single pass
    # ─────────────────────────────────────────────
    # Platypus flowables are stateful; rebuilding the same story twice can corrupt
    # table/paragraph layout. A single pass keeps the PDF deterministic.
    total_pages_est[0] = ""
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
