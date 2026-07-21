"""FYQ Smart Excel Import & Mapping Engine — integrity-first importer."""
import re, unicodedata
from difflib import SequenceMatcher
from decimal import Decimal, InvalidOperation

FIELD_MAP = {
'income': {
'revenue':['revenue','sales','net sales','operating revenue','total revenue','الإيرادات','الايرادات','إجمالي الإيرادات','اجمالي الايرادات','صافي المبيعات','المبيعات','إيرادات النشاط','ايرادات النشاط'],
'cogs':['cogs','cost of goods sold','cost of sales','cost of revenue','تكلفة البضاعة المباعة','تكلفة المبيعات','تكلفة الإيرادات','تكلفة الايرادات'],
'opex':['opex','operating expenses','operating expense','operating costs','المصاريف التشغيلية','مصروفات تشغيلية','المصروفات التشغيلية','تكاليف التشغيل'],
'depreciation':['depreciation','depreciation and amortization','d&a','الاستهلاك','الإهلاك','الاهلاك','استهلاك وإطفاء','الاستهلاك والإطفاء'],
'interest':['interest expense','finance cost','finance costs','interest','مصروف الفائدة','مصاريف الفائدة','تكاليف التمويل','مصاريف التمويل','فوائد'],
'tax_rate':['tax rate','tax %','income tax rate','معدل الضريبة','نسبة الضريبة','معدل ضريبة الدخل']},
'balance': {
'cash':['cash','cash and cash equivalents','cash equivalents','النقدية','النقد والنقد المعادل','النقدية وما يعادلها','نقد وما في حكمه'],
'accounts_receivable':['accounts receivable','trade receivables','receivables','debtors','الذمم المدينة','ذمم مدينين','ذمم المدينين','المدينون','العملاء'],
'inventory':['inventory','inventories','stock','المخزون','المخزون السلعي','بضاعة'],
'other_current_assets':['other current assets','prepayments and other current assets','أصول متداولة أخرى','اصول متداولة اخرى'],
'fixed_assets':['fixed assets','property plant and equipment','property, plant and equipment','ppe','pp&e','الأصول الثابتة','الاصول الثابتة','ممتلكات وآلات ومعدات'],
'accumulated_depreciation':['accumulated depreciation','مجمع الاستهلاك','مجمع الإهلاك','مجمع الاهلاك'],
'other_long_term_assets':['other non current assets','other non-current assets','other long term assets','أصول غير متداولة أخرى','اصول غير متداولة اخرى'],
'accounts_payable':['accounts payable','trade payables','payables','creditors','الذمم الدائنة','ذمم دائنين','ذمم الدائنين','الدائنون','الموردون'],
'short_term_debt':['short term debt','short-term debt','current borrowings','قروض قصيرة الأجل','قروض قصيرة الاجل','دين قصير الأجل'],
'other_current_liabilities':['other current liabilities','accruals and other current liabilities','التزامات متداولة أخرى','التزامات متداولة اخرى'],
'long_term_debt':['long term debt','long-term debt','non current borrowings','قروض طويلة الأجل','قروض طويلة الاجل','دين طويل الأجل'],
'other_long_term_liabilities':['other non current liabilities','other non-current liabilities','other long term liabilities','التزامات غير متداولة أخرى','التزامات غير متداولة اخرى'],
'paid_in_capital':['paid in capital','share capital','capital','رأس المال المدفوع','راس المال المدفوع','رأس المال'],
'retained_earnings':['retained earnings','accumulated profits','الأرباح المحتجزة','الارباح المحتجزة','أرباح مبقاة']},
'cashflow': {
'net_income':['net income','net profit','profit for the year','صافي الدخل','صافي الربح','ربح السنة'],
'depreciation_add_back':['depreciation add back','depreciation and amortization','depreciation','إهلاك واستهلاك','الاستهلاك المضاف','استهلاك مضاف','الإهلاك'],
'change_in_receivables':['change in receivables','change in accounts receivable','التغير في الذمم المدينة','تغير الذمم المدينة','تغيير في الذمم المدينة','تغيير في المدينين','التغير في المدينين','تغير المدينين'],
'change_in_inventory':['change in inventory','التغير في المخزون','تغير المخزون','تغيير في المخزون'],
'change_in_payables':['change in payables','change in accounts payable','التغير في الذمم الدائنة','تغير الذمم الدائنة','تغيير في الذمم الدائنة','تغيير في الدائنين','التغير في الدائنين','تغير الدائنين'],
'other_operating':['other operating','other operating activities','أنشطة تشغيلية أخرى','تدفقات تشغيلية أخرى'],
'capex':['capex','capital expenditure','capital expenditures','purchase of ppe','نفقات رأسمالية','نفقات رأسمالية capex','شراء أصول ثابتة'],
'asset_sales':['asset sales','proceeds from sale of assets','بيع أصول','متحصلات بيع الأصول'],
'other_investing':['other investing','other investing activities','أنشطة استثمارية أخرى'],
'debt_issued':['debt issued','new debt','borrowings proceeds','قروض جديدة','متحصلات قروض'],
'debt_repaid':['debt repaid','debt repayment','repayment of borrowings','سداد قروض','سداد الاقتراض'],
'dividends_paid':['dividends paid','dividends','توزيعات أرباح','توزيعات الارباح'],
'equity_issued':['equity issued','stock issuance','share issuance','إصدار أسهم','زيادة رأس المال'],
'other_financing':['other financing','other financing activities','أنشطة تمويلية أخرى'],
'beginning_cash':['beginning cash','opening cash','cash at beginning','رصيد بداية الفترة','رصيد اول الفترة','النقد أول الفترة']}}

SETTINGS_MAP={
'company':['company','company name','entity name','اسم الشركة','اسم المنشأة','الشركة'],
'year':['fiscal year','financial year','year','السنة المالية','السنه الماليه'],
'currency':['currency','العملة','العمله'],
'sector':['sector','industry','القطاع','النشاط']}
SECTION_HINTS={'income':['income','profit','loss','p&l','قائمة الدخل','الدخل','الأرباح والخسائر'], 'balance':['balance','financial position','bs','الميزانية','المركز المالي'], 'cashflow':['cash flow','cashflow','cf','التدفقات النقدية','التدفق النقدي'], 'settings':['settings','configuration','الإعدادات','الاعدادات']}
REQUIRED={'income':{'revenue','cogs','opex'},'balance':{'cash','accounts_receivable','inventory','accounts_payable','paid_in_capital','retained_earnings'},'cashflow':{'net_income','depreciation_add_back','capex','beginning_cash'}}


def norm(v):
    s=unicodedata.normalize('NFKC', str(v or '')).strip().lower()
    s=re.sub(r'[\u064b-\u065f\u0670]','',s).replace('ـ','')
    s=s.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ة','ه').replace('ى','ي')
    s=re.sub(r'[^\w%&]+',' ',s,flags=re.UNICODE)
    return re.sub(r'\s+',' ',s).strip()

def parse_num(v):
    if isinstance(v,(int,float,Decimal)) and not isinstance(v,bool): return float(v)
    if v is None: return None
    s=str(v).strip(); neg=s.startswith('(') and s.endswith(')'); s=s.strip('()')
    s=s.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩','0123456789'))
    s=s.replace('٬','').replace(',','').replace('،','').replace('ر.س','').replace('SAR','').replace('$','').replace('﷼','').replace('٪','').replace('%','').strip()
    try:
        n=float(Decimal(s)); return -n if neg else n
    except (InvalidOperation,ValueError): return None

def section_for_sheet(title):
    t=norm(title); best=(None,0)
    for sec,hints in SECTION_HINTS.items():
        score=max([SequenceMatcher(None,t,norm(h)).ratio() for h in hints]+[0])
        if any(norm(h) in t or t in norm(h) for h in hints): score=max(score,.9)
        if score>best[1]: best=(sec,score)
    return best[0] if best[1]>=.72 else None

def _best_alias(label, mapping):
    n=norm(label); best=(None,0)
    for field,aliases in mapping.items():
        for alias in aliases:
            a=norm(alias)
            score=1.0 if n==a else .94 if (a in n or n in a) and min(len(a),len(n))>=4 else SequenceMatcher(None,n,a).ratio()
            if score>best[1]: best=(field,score)
    return best

def match_label(label, section=None):
    n=norm(label); best=(None,None,0)
    sections=[section] if section in FIELD_MAP else FIELD_MAP.keys()
    for sec in sections:
        field,score=_best_alias(n,FIELD_MAP[sec])
        if score>best[2]: best=(sec,field,score)
    return best

def detect_year_columns(rows):
    out=[]
    for ri,row in enumerate(rows[:30]):
        for ci,v in enumerate(row):
            m=re.search(r'\b(20\d{2}|14\d{2})\b',str(v or ''))
            if m: out.append((ri,ci,m.group(1)))
    return out

def _adjacent_value(row, ci, numeric=True, selected_col=None):
    candidates=[]
    if selected_col is not None and selected_col<len(row): candidates.append((selected_col,row[selected_col]))
    for off in (1,-1,2,-2):
        j=ci+off
        if 0<=j<len(row): candidates.append((j,row[j]))
    candidates += [(j,v) for j,v in enumerate(row) if j!=ci]
    seen=set()
    for j,v in candidates:
        if j in seen: continue
        seen.add(j)
        if numeric:
            num=parse_num(v)
            if num is not None: return num,j
        elif v is not None and str(v).strip(): return str(v).strip(),j
    return None,None

def profile_workbook(wb):
    result={'income':{},'balance':{},'cashflow':{},'settings':{},'sheets_found':wb.sheetnames,'detected_fields':0,'mapped_fields':0,'validated_fields':0,'imported_fields':0,'mapping':[],'warnings':[],'missing_critical':[],'years_found':[],'selected_year':None,'confidence_score':0,'integrity_status':'REVIEW'}
    all_matches=[]; years=[]
    for ws in wb.worksheets:
        rows=[list(r) for r in ws.iter_rows(values_only=True)]
        sec_hint=section_for_sheet(ws.title); ycols=detect_year_columns(rows); years.extend(y for _,_,y in ycols)
        selected=max(ycols,key=lambda x:int(x[2])) if ycols else None; selected_col=selected[1] if selected else None
        if selected and (result['selected_year'] is None or int(selected[2])>int(result['selected_year'])): result['selected_year']=selected[2]
        for ri,row in enumerate(rows):
            for ci,label in enumerate(row):
                if label is None or parse_num(label) is not None: continue
                # Settings are strings and need a dedicated path.
                sfield,sscore=_best_alias(label,SETTINGS_MAP)
                if (sec_hint=='settings' or sscore>=.90) and sfield and sscore>=.72:
                    value,vcol=_adjacent_value(row,ci,numeric=False,selected_col=None)
                    if value is not None:
                        result['settings'][sfield]=value
                        result['mapping'].append({'section':'settings','field':sfield,'value':value,'label':str(label),'sheet':ws.title,'row':ri+1,'column':vcol+1 if vcol is not None else None,'confidence':round(sscore*100,1)})
                    continue
                sec,field,score=match_label(label,sec_hint)
                if not field or score<.72: continue
                result['detected_fields'] += 1
                value,vcol=_adjacent_value(row,ci,numeric=True,selected_col=selected_col)
                if value is None: continue
                if field=='tax_rate' and value<=1: value*=100
                # Cash-flow source template uses positive amounts for explicit outflow labels.
                if sec=='cashflow' and field in {'capex','debt_repaid','dividends_paid'} and value>0: value=-value
                all_matches.append({'section':sec,'field':field,'value':value,'label':str(label),'sheet':ws.title,'row':ri+1,'column':vcol+1 if vcol is not None else None,'confidence':round(score*100,1)})
    best={}
    for m in all_matches:
        key=(m['section'],m['field'])
        if key not in best or m['confidence']>best[key]['confidence']: best[key]=m
    for m in best.values(): result[m['section']][m['field']]=m['value']; result['mapping'].append(m)
    result['mapped_fields']=len(best)+len(result['settings']); result['imported_fields']=result['mapped_fields']
    result['years_found']=sorted(set(years))
    if result['selected_year'] and 'year' not in result['settings']: result['settings']['year']=result['selected_year']
    if 'year' in result['settings']: result['settings']['year']=str(result['settings']['year']).replace('.0','')
    confs=[m['confidence'] for m in result['mapping']]; result['confidence_score']=round(sum(confs)/len(confs),1) if confs else 0
    result['validated_fields']=sum(1 for m in best.values() if m['confidence']>=78)
    for sec,req in REQUIRED.items():
        for field in sorted(req-set(result[sec])): result['missing_critical'].append(f'{sec}.{field}')
    low=[m for m in result['mapping'] if m['confidence']<78]
    if low: result['warnings'].append(f'{len(low)} حقول بتطابق منخفض وتحتاج مراجعة')
    if result['years_found'] and len(result['years_found'])>1: result['warnings'].append(f"تم اكتشاف عدة سنوات واختيار أحدث سنة: {result['selected_year']}")
    if result['missing_critical']: result['warnings'].append('حقول حرجة مفقودة: '+', '.join(result['missing_critical']))
    result['integrity_status']='READY' if not result['missing_critical'] and result['confidence_score']>=78 else 'REVIEW'
    return result
