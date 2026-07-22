"""FYQ Smart Excel Import & Mapping Engine v2
Enterprise financial statement importer.
"""

import re
import unicodedata

from difflib import SequenceMatcher
from decimal import Decimal, InvalidOperation


# ============================================================
# FIELD MAPPING DATABASE
# ============================================================

FIELD_MAP = {

    "income": {

        "revenue": [
            "revenue",
            "sales",
            "net sales",
            "total revenue",
            "operating revenue",
            "الإيرادات",
            "الايرادات",
            "اجمالي الايرادات",
            "إجمالي الإيرادات",
            "المبيعات",
            "صافي المبيعات",
            "إيرادات النشاط",
            "ايرادات النشاط",
        ],

        "cogs": [
            "cogs",
            "cost of goods sold",
            "cost of sales",
            "cost of revenue",
            "تكلفة المبيعات",
            "تكلفة الإيرادات",
            "تكلفة الايرادات",
            "تكلفة البضاعة المباعة",
        ],

        "opex": [
            "opex",
            "operating expenses",
            "operating expense",
            "operating costs",
            "المصاريف التشغيلية",
            "المصروفات التشغيلية",
            "مصروفات تشغيلية",
            "تكاليف التشغيل",
        ],

        "depreciation": [
            "depreciation",
            "depreciation and amortization",
            "d&a",
            "الاستهلاك",
            "الإهلاك",
            "الاهلاك",
            "استهلاك وإطفاء",
            "الاستهلاك والإطفاء",
        ],

        "interest": [
            "interest",
            "interest expense",
            "finance cost",
            "finance costs",
            "مصروف الفائدة",
            "مصاريف الفائدة",
            "تكاليف التمويل",
            "مصاريف التمويل",
            "فوائد",
        ],

        "tax_rate": [
            "tax rate",
            "tax %",
            "income tax rate",
            "معدل الضريبة",
            "نسبة الضريبة",
            "معدل ضريبة الدخل",
        ],
    },


    "balance": {

        "cash": [
            "cash",
            "cash equivalents",
            "cash and cash equivalents",
            "النقدية",
            "النقد والنقد المعادل",
            "النقدية وما يعادلها",
            "نقد وما في حكمه",
        ],


        "accounts_receivable": [
            "accounts receivable",
            "trade receivables",
            "receivables",
            "debtors",
            "الذمم المدينة",
            "ذمم مدينين",
            "المدينون",
            "العملاء",
        ],


        "inventory": [
            "inventory",
            "inventories",
            "stock",
            "المخزون",
            "المخزون السلعي",
            "بضاعة",
        ],


        "fixed_assets": [
            "fixed assets",
            "property plant and equipment",
            "ppe",
            "pp&e",
            "الأصول الثابتة",
            "الاصول الثابتة",
            "ممتلكات وآلات ومعدات",
        ],


        "accounts_payable": [
            "accounts payable",
            "trade payables",
            "payables",
            "creditors",
            "الذمم الدائنة",
            "ذمم دائنين",
            "الدائنون",
            "الموردون",
        ],


        "short_term_debt": [
            "short term debt",
            "short-term debt",
            "current borrowings",
            "قروض قصيرة الاجل",
            "قروض قصيرة الأجل",
        ],


        "other_current_liabilities": [
            "other current liabilities",
            "التزامات متداولة أخرى",
            "التزامات متداولة اخرى",
        ],


        "long_term_debt": [
            "long term debt",
            "long-term debt",
            "non current borrowings",
            "قروض طويلة الأجل",
            "قروض طويلة الاجل",
        ],


        "paid_in_capital": [
            "paid in capital",
            "share capital",
            "capital",
            "رأس المال المدفوع",
            "راس المال المدفوع",
            "رأس المال",
            "راس المال",
            "رأس مال",
            "راس مال",
        ],


        "retained_earnings": [
            "retained earnings",
            "accumulated profits",
            "الأرباح المحتجزة",
            "الارباح المحتجزة",
            "أرباح مبقاة",
        ],

    },


    "cashflow": {

        "net_income": [
            "net income",
            "net profit",
            "profit for the year",
            "صافي الدخل",
            "صافي الربح",
            "ربح السنة",
        ],

        "depreciation_add_back": [
            "depreciation add back",
            "depreciation",
            "depreciation and amortization",
            "الاستهلاك المضاف",
            "استهلاك مضاف",
            "الإهلاك",
        ],

        "change_in_receivables": [
            "change in receivables",
            "change in accounts receivable",
            "تغير الذمم المدينة",
            "التغير في الذمم المدينة",
        ],

        "change_in_inventory": [
            "change in inventory",
            "تغير المخزون",
            "التغير في المخزون",
        ],

        "change_in_payables": [
            "change in payables",
            "change in accounts payable",
            "تغير الذمم الدائنة",
            "التغير في الذمم الدائنة",
        ],

        "capex": [
            "capex",
            "capital expenditure",
            "capital expenditures",
            "purchase of ppe",
            "نفقات رأسمالية",
            "شراء أصول ثابتة",
        ],

        "debt_issued": [
            "debt issued",
            "new debt",
            "borrowings proceeds",
            "قروض جديدة",
        ],

        "debt_repaid": [
            "debt repaid",
            "debt repayment",
            "سداد قروض",
        ],

        "dividends_paid": [
            "dividends paid",
            "dividends",
            "توزيعات الأرباح",
        ],

        "beginning_cash": [
            "beginning cash",
            "opening cash",
            "cash at beginning",
            "رصيد بداية الفترة",
            "بداية النقد",
            "بداية الفترة النقدية",
            "النقد أول الفترة",
        ],
    }
}
# ============================================================
# SETTINGS + SHEET DETECTION
# ============================================================

SETTINGS_MAP = {

    "company": [
        "company",
        "company name",
        "entity name",
        "اسم الشركة",
        "اسم المنشأة",
        "الشركة",
    ],

    "year": [
        "fiscal year",
        "financial year",
        "year",
        "السنة المالية",
        "السنه الماليه",
    ],

    "currency": [
        "currency",
        "العملة",
        "العمله",
    ],

    "sector": [
        "sector",
        "industry",
        "القطاع",
        "النشاط",
    ]
}


SECTION_HINTS = {

    "income": [
        "income",
        "profit",
        "loss",
        "p&l",
        "profit and loss",
        "قائمة الدخل",
        "الدخل",
        "الأرباح والخسائر",
    ],

    "balance": [
        "balance",
        "financial position",
        "balance sheet",
        "bs",
        "الميزانية",
        "المركز المالي",
    ],

    "cashflow": [
        "cash flow",
        "cashflow",
        "cf",
        "التدفقات النقدية",
        "التدفق النقدي",
    ],

    "settings": [
        "settings",
        "configuration",
        "الإعدادات",
        "الاعدادات",
    ]
}


REQUIRED = {

    "income": {
        "revenue",
        "cogs",
        "opex"
    },

    "balance": {
        "cash",
        "accounts_receivable",
        "inventory",
        "accounts_payable",
        "paid_in_capital",
        "retained_earnings"
    },

    "cashflow": {
        "net_income",
        "depreciation_add_back",
        "capex",
        "beginning_cash"
    }
}


# ============================================================
# NORMALIZATION
# ============================================================


def norm(value):

    text = unicodedata.normalize(
        "NFKC",
        str(value or "")
    ).strip().lower()


    text = re.sub(
        r"[\u064b-\u065f\u0670]",
        "",
        text
    )


    text = (
        text
        .replace("أ","ا")
        .replace("إ","ا")
        .replace("آ","ا")
        .replace("ة","ه")
        .replace("ى","ي")
    )


    text = text.replace("ـ","")


    text = re.sub(
        r"[^\w%&]+",
        " ",
        text,
        flags=re.UNICODE
    )


    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()



# ============================================================
# NUMBER PARSER
# ============================================================


def parse_num(value):

    if isinstance(
        value,
        (int,float,Decimal)
    ) and not isinstance(value,bool):

        return float(value)


    if value is None:
        return None


    text = str(value).strip()


    negative = (
        text.startswith("(")
        and text.endswith(")")
    )


    text = text.strip("()")


    text = text.translate(
        str.maketrans(
            "٠١٢٣٤٥٦٧٨٩",
            "0123456789"
        )
    )


    text = (
        text
        .replace(",","")
        .replace("٬","")
        .replace("،","")
        .replace("SAR","")
        .replace("ر.س","")
        .replace("%","")
        .replace("٪","")
        .replace("$","")
        .replace("﷼","")
    )


    try:

        number = float(
            Decimal(text)
        )

        return -number if negative else number


    except (
        InvalidOperation,
        ValueError
    ):

        return None



# ============================================================
# SHEET CLASSIFIER
# ============================================================


def section_for_sheet(title):

    name = norm(title)

    best = (
        None,
        0
    )


    for section, hints in SECTION_HINTS.items():

        for hint in hints:

            score = SequenceMatcher(
                None,
                name,
                norm(hint)
            ).ratio()


            if norm(hint) in name:

                score = max(
                    score,
                    0.95
                )


            if score > best[1]:

                best = (
                    section,
                    score
                )


    return (
        best[0]
        if best[1] >= 0.65
        else None
    )



# ============================================================
# FIELD MATCHING
# ============================================================


def best_alias(label, mapping):

    name = norm(label)

    result = (
        None,
        0
    )


    for field, aliases in mapping.items():

        for alias in aliases:

            a = norm(alias)


            if name == a:

                score = 1


            elif (
                a in name
                or name in a
            ):

                score = 0.94


            else:

                score = SequenceMatcher(
                    None,
                    name,
                    a
                ).ratio()



            if score > result[1]:

                result = (
                    field,
                    score
                )

    return result



def match_label(
        label,
        section=None
):

    best = (
        None,
        None,
        0
    )


    sections = (
        [section]
        if section in FIELD_MAP
        else FIELD_MAP.keys()
    )


    for sec in sections:

        field,score = best_alias(
            label,
            FIELD_MAP[sec]
        )


        if score > best[2]:

            best = (
                sec,
                field,
                score
            )


    return best



def adjacent_value(
        row,
        index
):

    candidates = []


    for offset in (
        1,
        -1,
        2,
        -2
    ):

        pos = index + offset

        if (
            pos >= 0
            and pos < len(row)
        ):

            candidates.append(
                row[pos]
            )


    for item in candidates:

        number = parse_num(item)

        if number is not None:

            return number


    return None
# ============================================================
# MAIN WORKBOOK PROFILER
# ============================================================

def profile_workbook(wb):

    result = {

        "income": {},
        "balance": {},
        "cashflow": {},
        "settings": {},

        "sheets_found": wb.sheetnames,

        "detected_fields": 0,
        "mapped_fields": 0,
        "validated_fields": 0,
        "imported_fields": 0,

        "mapping": [],

        "warnings": [],

        "missing_critical": [],

        "years_found": [],

        "selected_year": None,

        "confidence_score": 0,

        "data_quality_score": 0,

        "financial_health": {},

        "integrity_status": "REVIEW"
    }



    matches = []

    years = []



    # --------------------------------------------------------
    # READ ALL SHEETS
    # --------------------------------------------------------

    for ws in wb.worksheets:


        section_hint = section_for_sheet(
            ws.title
        )


        rows = [
            list(row)
            for row in ws.iter_rows(
                values_only=True
            )
        ]



        for row_index,row in enumerate(rows):

            for col_index,label in enumerate(row):


                if (
                    label is None
                    or parse_num(label) is not None
                ):
                    continue



                # SETTINGS

                setting,score = best_alias(
                    label,
                    SETTINGS_MAP
                )


                if (
                    setting
                    and score >= 0.72
                ):

                    # SETTINGS protection:
                    # Never classify financial statement labels as settings
                    blocked_settings_labels = [
                        "رأس المال",
                        "راس المال",
                        "capital",
                        "share capital",
                        "paid in capital",
                        "الإيرادات",
                        "الايرادات",
                        "المبيعات",
                        "النقد",
                        "المخزون"
                    ]

                    if any(
                        norm(x) in norm(label)
                        for x in blocked_settings_labels
                    ):
                        setting = None


                if (
                    setting
                    and score >= 0.72
                ):


                    value = None


                    if col_index + 1 < len(row):

                        value = row[
                            col_index + 1
                        ]


                    # Prevent financial amounts from being detected as years
                    if setting == "year":
                        try:
                            year_value = int(float(value))
                            if not (1900 <= year_value <= 2100):
                                continue
                        except Exception:
                            continue


                    if value:

                        result["settings"][
                            setting
                        ] = str(value)



                        result["mapping"].append({

                            "section":"settings",
                            "field":setting,
                            "label":str(label),
                            "value":str(value),
                            "sheet":ws.title,
                            "row":row_index+1,
                            "confidence":round(
                                score*100,
                                1
                            )
                        })

                    continue




                # FINANCIAL FIELDS

                section,field,score = match_label(
                    label,
                    section_hint
                )


                if (
                    not field
                    or score < 0.72
                ):

                    continue



                result[
                    "detected_fields"
                ] += 1



                value = adjacent_value(
                    row,
                    col_index
                )


                if value is None:
                    continue



                if (
                    field=="tax_rate"
                    and value <= 1
                ):

                    value *= 100



                if (
                    section=="cashflow"
                    and field in [
                        "capex",
                        "debt_repaid",
                        "dividends_paid"
                    ]
                    and value > 0
                ):

                    value = -value




                matches.append({

                    "section":section,

                    "field":field,

                    "value":value,

                    "label":str(label),

                    "sheet":ws.title,

                    "row":row_index+1,

                    "confidence":round(
                        score*100,
                        1
                    )

                })



    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    selected = {}

    for item in matches:


        key = (
            item["section"],
            item["field"]
        )


        if (
            key not in selected
            or item["confidence"]
            >
            selected[key]["confidence"]
        ):

            selected[key] = item




    for item in selected.values():

        result[
            item["section"]
        ][
            item["field"]
        ] = item["value"]


        result["mapping"].append(
            item
        )




    # --------------------------------------------------------
    # COUNTS
    # --------------------------------------------------------

    result["mapped_fields"] = len(
        selected
    ) + len(
        result["settings"]
    )


    result["imported_fields"] = (
        result["mapped_fields"]
    )



    confidence = [

        x["confidence"]

        for x in result["mapping"]

    ]


    if confidence:

        result["confidence_score"] = round(
            sum(confidence)
            /
            len(confidence),
            1
        )




    result["validated_fields"] = sum(

        1

        for x in selected.values()

        if x["confidence"] >= 78

    )




    # --------------------------------------------------------
    # MISSING REQUIRED DATA
    # --------------------------------------------------------

    for section,fields in REQUIRED.items():

        for field in fields:


            if field not in result[section]:

                result["missing_critical"].append(
                    f"{section}.{field}"
                )




    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    quality = 0


    if result["mapped_fields"]:

        quality += (
            result["mapped_fields"]
            /
            28
            *
            60
        )


    quality += (
        result["confidence_score"]
        *
        0.4
    )



    result["data_quality_score"] = round(
        min(quality,100),
        1
    )




    # --------------------------------------------------------
    # BALANCE CHECK
    # --------------------------------------------------------

    assets = sum([

        result["balance"].get(
            "cash",
            0
        ),

        result["balance"].get(
            "accounts_receivable",
            0
        ),

        result["balance"].get(
            "inventory",
            0
        ),

        result["balance"].get(
            "fixed_assets",
            0
        )

    ])



    liabilities_equity = sum([

        result["balance"].get(
            "accounts_payable",
            0
        ),

        result["balance"].get(
            "short_term_debt",
            0
        ),

        result["balance"].get(
            "long_term_debt",
            0
        ),

        result["balance"].get(
            "other_current_liabilities",
            0
        ),

        result["balance"].get(
            "paid_in_capital",
            0
        ),

        result["balance"].get(
            "retained_earnings",
            0
        )

    ])



    difference = round(
        assets-liabilities_equity,
        2
    )



    result["financial_health"] = {

        "assets":

        assets,


        "liabilities_equity":

        liabilities_equity,


        "balance_difference":

        difference,


        "balanced":

        abs(difference) < 1

    }




    if abs(difference) >= 1:

        result["warnings"].append(
            "الميزانية غير متوازنة"
        )







    low = [

        x

        for x in result["mapping"]

        if x["confidence"] < 78

    ]



    if low:

        result["warnings"].append(
            f"{len(low)} حقول تحتاج مراجعة"
        )




    
    # --------------------------------------------------------
    # BEGINNING CASH NORMALIZATION
    # --------------------------------------------------------

    cf = result["cashflow"]

    # Ignore invalid imported opening cash
    if cf.get("beginning_cash", 0) < 0:
        cf.pop("beginning_cash", None)

    beginning = cf.get(
        "beginning_cash"
    )


    if beginning is None:

        cfo = (
            cf.get("net_income",0)
            + cf.get("depreciation_add_back",0)
            + cf.get("change_in_receivables",0)
            + cf.get("change_in_inventory",0)
            + cf.get("change_in_payables",0)
        )

        capex = cf.get(
            "capex",
            0
        )

        ending_cash = result["balance"].get(
            "cash",
            0
        )


        # Derive opening cash:
        # Ending Cash = Beginning Cash + CFO + CFI + CFF
        # Therefore:
        # Beginning Cash = Ending Cash - CFO - CFI - CFF

        cfi = capex

        beginning_cash = (
            ending_cash - cfo - cfi
        )

        # Never allow invalid negative opening cash
        if beginning_cash < 0:
            beginning_cash = 0

        result["cashflow"]["beginning_cash"] = (
            beginning_cash
        )


    if "cashflow.beginning_cash" in result["missing_critical"]:

        result["missing_critical"].remove(
            "cashflow.beginning_cash"
        )


# --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    if (

        not result["missing_critical"]

        and

        result["confidence_score"] >= 78

    ):

        result["integrity_status"] = "READY"


    else:

        result["integrity_status"] = "REVIEW"




    # FINAL MISSING DATA WARNING

    if result["missing_critical"]:

        if "بيانات حرجة ناقصة" not in result["warnings"]:

            result["warnings"].append(
                "بيانات حرجة ناقصة"
            )


    return result