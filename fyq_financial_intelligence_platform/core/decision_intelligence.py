"""FYQ decision-intelligence services.
Decimal-safe canonical calculations, validation, executive narrative, scenarios and benchmarks.
"""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from dataclasses import dataclass
from typing import Any

ZERO = Decimal('0')
HUNDRED = Decimal('100')
MONEY_Q = Decimal('0.01')
RATIO_Q = Decimal('0.0001')

def D(value: Any, default='0') -> Decimal:
    if value in (None, '', 'null'): return Decimal(default)
    try: return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError): raise ValueError(f'قيمة رقمية غير صالحة: {value}')

def money(v): return D(v).quantize(MONEY_Q, rounding=ROUND_HALF_UP)
def ratio(v): return D(v).quantize(RATIO_Q, rounding=ROUND_HALF_UP)
def pct(n, d): return ratio((D(n) / D(d) * HUNDRED) if D(d) else ZERO)
def js(v):
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, dict): return {k: js(x) for k,x in v.items()}
    if isinstance(v, list): return [js(x) for x in v]
    return v

def canonical(income, balance, cashflow=None):
    i = {k:D(v) for k,v in (income or {}).items()}
    b = {k:D(v) for k,v in (balance or {}).items()}
    c = {k:D(v) for k,v in (cashflow or {}).items()}
    revenue=D(i.get('revenue')); cogs=D(i.get('cogs', i.get('cost_of_goods_sold'))); opex=D(i.get('opex', i.get('operating_expenses')))
    dep=D(i.get('depreciation')); interest=D(i.get('interest', i.get('interest_expense'))); tax_rate=D(i.get('tax_rate',15)); tax_rate=tax_rate/HUNDRED if tax_rate>1 else tax_rate
    gp=revenue-cogs; ebitda=gp-opex; ebit=ebitda-dep; ebt=ebit-interest; tax=max(ZERO, ebt*tax_rate); ni=ebt-tax
    ca=sum(D(b.get(k)) for k in ['cash','accounts_receivable','inventory','other_current_assets'])
    nfa=D(b.get('fixed_assets'))-D(b.get('accumulated_depreciation')); assets=ca+nfa+D(b.get('other_long_term_assets'))
    cl=sum(D(b.get(k)) for k in ['accounts_payable','short_term_debt','other_current_liabilities'])
    liabilities=cl+D(b.get('long_term_debt'))+D(b.get('other_long_term_liabilities')); equity=D(b.get('paid_in_capital'))+D(b.get('retained_earnings'))
    wc = D(c.get('change_in_working_capital')) if 'change_in_working_capital' in c else (D(c.get('change_in_receivables'))+D(c.get('change_in_inventory'))+D(c.get('change_in_payables')))
    ocf=(D(c.get('net_income',ni))+D(c.get('depreciation_add_back'))+wc+D(c.get('other_operating'))) if cashflow else ZERO
    capex = -abs(D(c.get('capex'))) if cashflow else ZERO
    fcf=ocf+capex if cashflow else ZERO
    debt=D(b.get('short_term_debt'))+D(b.get('long_term_debt'))
    metrics={'revenue':revenue,'gross_profit':gp,'ebitda':ebitda,'ebit':ebit,'net_income':ni,'gross_margin':pct(gp,revenue),'ebitda_margin':pct(ebitda,revenue),'net_margin':pct(ni,revenue),'total_assets':assets,'current_assets':ca,'current_liabilities':cl,'total_liabilities':liabilities,'total_equity':equity,'current_ratio':ratio(ca/cl) if cl else ZERO,'debt_to_equity':ratio(debt/equity) if equity else ZERO,'debt_to_assets':ratio(debt/assets) if assets else ZERO,'liabilities_to_equity':ratio(liabilities/equity) if equity else ZERO,'liabilities_to_assets':ratio(liabilities/assets) if assets else ZERO,'net_debt_to_ebitda':ratio((debt-D(b.get('cash')))/ebitda) if ebitda else ZERO,'debt_to_ebitda':ratio(debt/ebitda) if ebitda else ZERO,'interest_coverage':ratio(ebit/interest) if interest > ZERO else ZERO,'roa':pct(ni,assets),'roe':pct(ni,equity),'operating_cash_flow':ocf,'free_cash_flow':fcf,'ending_cash':(D(c.get('beginning_cash')) + ocf + capex + D(c.get('asset_sales')) + D(c.get('other_investing')) + D(c.get('debt_issued')) - abs(D(c.get('debt_repaid'))) - abs(D(c.get('dividends_paid'))) + D(c.get('equity_issued')) + D(c.get('other_financing'))) if cashflow else ZERO,'balance_cash':D(b.get('cash')),'balance_difference':assets-(liabilities+equity)}
    return metrics

def validate_payload(income, balance, cashflow=None):
    issues=[]; required_i=['revenue','cogs','opex']; required_b=['cash','accounts_receivable','inventory','accounts_payable','paid_in_capital','retained_earnings']
    def add(level, code, msg, field=None): issues.append({'level':level,'code':code,'message':msg,'field':field})
    for k in required_i:
        if k not in (income or {}) and ({'cogs':'cost_of_goods_sold','opex':'operating_expenses'}.get(k) not in (income or {})): add('CRITICAL','MISSING_FIELD',f'الحقل المالي المطلوب غير موجود: {k}',k)
    for k in required_b:
        if k not in (balance or {}): add('CRITICAL','MISSING_FIELD',f'الحقل المالي المطلوب غير موجود: {k}',k)
    if cashflow:
        for k in ['net_income','depreciation_add_back','capex','beginning_cash']:
            if k not in cashflow: add('CRITICAL','MISSING_FIELD',f'حقل تدفقات نقدية مطلوب غير موجود: {k}',k)
    try: m=canonical(income,balance,cashflow)
    except ValueError as e: add('CRITICAL','INVALID_NUMBER',str(e)); return {'score':0,'status':'BLOCKED','issues':issues,'can_analyze':False}
    tolerance=max(Decimal('1.00'), abs(m['total_assets'])*Decimal('0.0001'))
    if abs(m['balance_difference']) > tolerance: add('CRITICAL','UNBALANCED',f"الميزانية غير متوازنة. الفرق {money(m['balance_difference'])}. التقييم النهائي محجوب حتى تصحيح البيانات.",'balance')
    if cashflow:
        cash_gap = m['balance_cash'] - m['ending_cash']
        cash_tolerance=max(Decimal('1.00'), abs(m['balance_cash'])*Decimal('0.0001'))
        if abs(cash_gap) > cash_tolerance:
            add('CRITICAL','CASH_RECONCILIATION_MISMATCH',f"رصيد النقد في الميزانية لا يطابق رصيد النقد الختامي في قائمة التدفقات. الفرق {money(cash_gap)}.",'cash')
    if m['revenue'] < 0: add('WARNING','NEGATIVE_REVENUE','الإيرادات سالبة؛ راجع طبيعة الفترة أو البيانات.','revenue')
    if m['total_assets'] <= 0: add('CRITICAL','INVALID_ASSETS','إجمالي الأصول يجب أن يكون أكبر من صفر.','total_assets')
    if cashflow:
        cfni=D((cashflow or {}).get('net_income',m['net_income']))
        ni_gap = cfni - m['net_income']
        ni_tolerance=max(Decimal('1.00'), abs(m['net_income'])*Decimal('0.0001'))
        if abs(ni_gap) > ni_tolerance:
            add('CRITICAL','NI_RECONCILIATION_MISMATCH',
                f"صافي الدخل في قائمة التدفقات لا يطابق صافي الدخل المحسوب من قائمة الدخل. "
                f"صافي دخل قائمة الدخل {money(m['net_income'])}، وصافي الدخل المستخدم في التدفقات {money(cfni)}، "
                f"والفرق {money(ni_gap)}. التقييم النهائي محجوب حتى تصحيح البيانات.",
                'net_income')
    numeric=[]
    for section in [income or {},balance or {},cashflow or {}]:
        for k,v in section.items():
            try: numeric.append((k,abs(D(v))))
            except ValueError: add('CRITICAL','INVALID_NUMBER',f'قيمة غير رقمية في {k}',k)
    vals=[v for _,v in numeric if v>0]
    if vals:
        med=sorted(vals)[len(vals)//2]
        for k,v in numeric:
            if med and v > med*Decimal('10000'): add('WARNING','EXTREME_VALUE',f'قيمة مرتفعة جدًا مقارنة ببقية البيانات: {k}',k)
    penalty=sum(35 if x['level']=='CRITICAL' else 8 if x['level']=='WARNING' else 1 for x in issues); score=max(0,100-penalty); blocked=any(x['level']=='CRITICAL' for x in issues)
    return {'score':score,'status':'BLOCKED' if blocked else ('REVIEW' if issues else 'READY'),'issues':issues,'can_analyze':not blocked,'metrics':js(m)}

def health_components(m):
    def band(v, low, good): return Decimal('30') if v<low else Decimal('65') if v<good else Decimal('90')
    liq=band(m['current_ratio'],Decimal('1'),Decimal('1.5'))
    prof=band(m['net_margin'],Decimal('5'),Decimal('12'))
    lev=Decimal('90') if m['debt_to_equity']<=Decimal('1') else Decimal('65') if m['debt_to_equity']<=Decimal('2') else Decimal('30')
    eff=band(m['roa'],Decimal('3'),Decimal('8'))
    cash=Decimal('90') if m['operating_cash_flow']>0 else Decimal('30')
    total=liq*Decimal('.2')+prof*Decimal('.25')+lev*Decimal('.2')+eff*Decimal('.15')+cash*Decimal('.2')
    return {'liquidity':liq,'profitability':prof,'leverage':lev,'efficiency':eff,'cashflow':cash,'score':total}


def executive_linkages(m, cashflow_present=False, integrity_unreliable=False):
    """Explain causal links between financial metrics for an executive reader."""
    links=[]
    def add(level, title, cause, effect, action):
        links.append({'level':level,'title':title,'cause':cause,'effect':effect,'action':action})

    if m['net_margin'] < ZERO:
        add('critical','الربحية التشغيلية تحت ضغط',
            f"هامش صافي الدخل {m['net_margin'].quantize(Decimal('.1'))}%، ما يعني أن التكاليف والفوائد والضريبة تستهلك الإيراد بالكامل.",
            'كل نمو في المبيعات غير المصحوب بتحسين الهامش قد يزيد حجم التشغيل دون خلق قيمة نقدية.',
            'فصل أثر التسعير وتكلفة المبيعات والمصاريف التشغيلية قبل اعتماد أي توسع.')
    elif m['net_margin'] < Decimal('5'):
        add('warning','الهامش محدود أمام الصدمات',
            f"هامش صافي الربح {m['net_margin'].quantize(Decimal('.1'))}% يترك مساحة ضيقة لامتصاص ارتفاع التكلفة أو التمويل.",
            'أي انحراف محدود في تكلفة المبيعات أو مصروفات الفائدة قد ينتقل بسرعة إلى صافي الدخل.',
            'مراجعة محركات التسعير والشراء والمصاريف الثابتة مع تحديد حد أدنى للهامش.')
    else:
        add('good','الربحية تمنح مساحة قرار',
            f"هامش صافي الربح {m['net_margin'].quantize(Decimal('.1'))}% يوفر قدرة أفضل على امتصاص تقلبات التكلفة.",
            'يمكن توجيه جزء من العائد إلى السيولة أو الاستثمار بعد التحقق من جودة التحول النقدي.',
            'حماية عناصر التسعير والكفاءة التي تدعم الهامش عند إعداد الموازنة القادمة.')

    if cashflow_present:
        if m['net_income'] > ZERO and m['operating_cash_flow'] <= ZERO:
            add('critical','الربح المحاسبي لا يتحول إلى نقد',
                f"صافي الدخل موجب ({money(m['net_income'])}) بينما التدفق التشغيلي {money(m['operating_cash_flow'])}.",
                'يرفع ذلك الاعتماد على تمويل قصير الأجل وقد يضغط السيولة حتى مع ظهور أرباح في قائمة الدخل.',
                'تفكيك تغيرات الذمم والمخزون وربطها بخطة تحصيل أسبوعية وحدود ائتمانية واضحة.')
        elif m['operating_cash_flow'] > ZERO and m['free_cash_flow'] < ZERO:
            add('warning','التشغيل يولد نقدًا لكن الاستثمار يستهلكه',
                f"التدفق التشغيلي {money(m['operating_cash_flow'])} موجب، بينما التدفق الحر {money(m['free_cash_flow'])} سالب.",
                'يؤخر ذلك قدرة المنشأة على خفض الدين أو تمويل النمو ذاتيًا، ويزيد حساسية قرارات الإنفاق الرأسمالي.',
                'ترتيب مشروعات CAPEX بحسب العائد النقدي وتوقيت الإنفاق قبل اللجوء إلى تمويل إضافي.')
        elif m['operating_cash_flow'] > ZERO and m['free_cash_flow'] > ZERO:
            add('good','الربحية مدعومة بتحول نقدي',
                f"التدفق التشغيلي {money(m['operating_cash_flow'])} والتدفق الحر {money(m['free_cash_flow'])} موجبان.",
                'يوفر ذلك مرونة أكبر لتمويل النمو أو خفض المديونية دون استنزاف السيولة التشغيلية.',
                'تحديد ترتيب استخدام النقد بين خفض الدين والاحتياطي والاستثمار وفق العائد والمخاطر.')

    if not integrity_unreliable:
        if m['current_ratio'] < Decimal('1'):
            add('critical','ضغط رأس المال العامل يضاعف المخاطر',
                f"نسبة التداول {m['current_ratio'].quantize(Decimal('.2'))} مرة، أي أن الأصول المتداولة أقل من الالتزامات قصيرة الأجل.",
                'أي تأخر في التحصيل أو زيادة في المخزون قد يخلق فجوة نقدية ويستدعي تمويلًا مكلفًا.',
                'ربط دورة التحصيل والمخزون وجدولة الدائنين بلوحة سيولة دورية قبل الالتزامات الجوهرية.')
        elif m['current_ratio'] < Decimal('1.5'):
            add('warning','السيولة قابلة للتحسن وليست فائضة',
                f"نسبة التداول {m['current_ratio'].quantize(Decimal('.2'))} مرة تقع في نطاق يحتاج متابعة رأس المال العامل.",
                'التمويل أو الاستثمار الجديد ينبغي أن يراعي أثره على الالتزامات القصيرة الأجل والنقد المتاح.',
                'وضع حد تشغيلي للسيولة ومتابعة الذمم والمخزون مقابل التزامات الثلاثة أشهر القادمة.')
        if m['debt_to_equity'] > Decimal('2'):
            add('critical','الرفع المالي يحد من مرونة القرار',
                f"الدين إلى حقوق الملكية {m['debt_to_equity'].quantize(Decimal('.2'))} مرة.",
                'ارتفاع الدين يضخم أثر الفائدة على صافي الدخل ويقلص مساحة امتصاص الصدمات التشغيلية.',
                'اختبار السيناريو الضاغط قبل زيادة الاقتراض ومقارنة سداد الدين بعائد الاستثمار المتوقع.')
        elif m['debt_to_equity'] > Decimal('1'):
            add('warning','التمويل يتطلب انضباطًا إضافيًا',
                f"الدين إلى حقوق الملكية {m['debt_to_equity'].quantize(Decimal('.2'))} مرة.",
                'يزداد تأثير تغير تكلفة التمويل على الربحية والقدرة على الحفاظ على السيولة.',
                'ربط أي تمويل جديد بتدفقات نقدية قابلة للقياس وحدود واضحة لخدمة الدين.')

    return links[:5]

def executive_summary(income,balance,cashflow=None):
    v=validate_payload(income,balance,cashflow)
    m=canonical(income,balance,cashflow)
    blocking_codes={x.get('code') for x in v.get('issues',[]) if x.get('level')=='CRITICAL'}
    # A balance mismatch invalidates balance-dependent scoring, but must not erase
    # reliable income/cash-flow readouts. The executive summary therefore degrades
    # to a governed provisional readout instead of failing the endpoint.
    balance_unreliable='UNBALANCED' in blocking_codes or 'INVALID_ASSETS' in blocking_codes
    cash_unreliable='CASH_RECONCILIATION_MISMATCH' in blocking_codes
    ni_unreliable='NI_RECONCILIATION_MISMATCH' in blocking_codes
    integrity_unreliable=balance_unreliable or cash_unreliable or ni_unreliable
    fatal=blocking_codes-{'UNBALANCED','CASH_RECONCILIATION_MISMATCH','NI_RECONCILIATION_MISMATCH'}
    if fatal:
        raise ValueError('البيانات الأساسية غير كافية لإنشاء قراءة تنفيذية موثوقة')

    strengths=[]; weaknesses=[]; risks=[]
    if m['net_margin']>=12: strengths.append(f"هامش صافي ربح قوي يبلغ {m['net_margin'].quantize(Decimal('.1'))}%")
    else: weaknesses.append(f"هامش صافي الربح عند {m['net_margin'].quantize(Decimal('.1'))}% ويحتاج مراجعة هيكل التكلفة والتسعير")
    if m['operating_cash_flow']>0: strengths.append(f"التدفق النقدي التشغيلي موجب بقيمة {money(m['operating_cash_flow'])}")
    else: risks.append('التدفق النقدي التشغيلي غير إيجابي رغم الأداء المحاسبي')
    if m['free_cash_flow']>0: strengths.append(f"التدفق النقدي الحر موجب بقيمة {money(m['free_cash_flow'])}")
    elif cashflow: weaknesses.append('التدفق النقدي الحر غير موجب ويحتاج مراجعة الإنفاق الرأسمالي')

    if not integrity_unreliable:
        h=health_components(m)
        if m['current_ratio']>=Decimal('1.5'): strengths.append(f"سيولة مريحة بنسبة تداول {m['current_ratio'].quantize(Decimal('.01'))} مرة")
        elif m['current_ratio']<1: risks.append('ضغط سيولة محتمل وقدرة محدودة على تغطية الالتزامات قصيرة الأجل')
        else: weaknesses.append('السيولة مقبولة لكنها تحتاج متابعة لرأس المال العامل')
        if m['debt_to_equity']>2: risks.append(f"رفع مالي مرتفع؛ الدين إلى حقوق الملكية {m['debt_to_equity'].quantize(Decimal('.01'))} مرة")
        score=h['score'].quantize(Decimal('.1'))
        label='ممتاز' if score>=90 else 'جيد جدًا' if score>=80 else 'جيد' if score>=70 else 'مقبول' if score>=60 else 'يحتاج معالجة'
        narrative=f"يبلغ تقييم الصحة المالية {score}/100 ({label}). حققت المنشأة إيرادات {money(m['revenue'])} وصافي دخل {money(m['net_income'])} بهامش {m['net_margin'].quantize(Decimal('.1'))}%."
        status='FINAL'; components=h
    else:
        score=None; label='مبدئي — مراجعة سلامة الميزانية'
        components=None; status='PROVISIONAL'
        integrity_reasons=[]
        if balance_unreliable:
            integrity_reasons.append(f"فرق الميزانية {money(m['balance_difference'])}")
            risks.insert(0, f"فرق الميزانية {money(m['balance_difference'])}؛ تم حجب المؤشرات المعتمدة على سلامة المركز المالي")
        if cash_unreliable:
            cash_gap=m['balance_cash']-m['ending_cash']
            integrity_reasons.append(f"فرق مطابقة النقد {money(cash_gap)}")
            risks.insert(0, f"رصيد النقد في الميزانية يختلف عن النقد الختامي في التدفقات بمقدار {money(cash_gap)}")
        if ni_unreliable:
            cfni=D((cashflow or {}).get('net_income',m['net_income']))
            ni_gap=cfni-m['net_income']
            integrity_reasons.append(f"فرق صافي الدخل بين قائمتي الدخل والتدفقات {money(ni_gap)}")
            risks.insert(0, f"صافي الدخل المستخدم في التدفقات يختلف عن قائمة الدخل بمقدار {money(ni_gap)}")
        narrative=(f"النتائج التشغيلية متاحة للقراءة المبدئية. حققت المنشأة إيرادات {money(m['revenue'])} وصافي دخل {money(m['net_income'])} " f"وتدفقًا تشغيليًا محسوبًا بقيمة {money(m['operating_cash_flow'])} وتدفقًا نقديًا حرًا {money(m['free_cash_flow'])}. " f"تم حجب التقييم المالي النهائي بسبب: {'، '.join(integrity_reasons)}.")

    priorities=[]
    if balance_unreliable: priorities.append('تصحيح فرق الميزانية وإعادة مطابقة الأصول مع الالتزامات وحقوق الملكية')
    if cash_unreliable: priorities.append('مطابقة رصيد النقد الختامي في قائمة التدفقات مع بند النقد وما في حكمه في الميزانية')
    if ni_unreliable: priorities.append('مطابقة صافي الدخل المستخدم في قائمة التدفقات مع صافي الدخل المحسوب من قائمة الدخل')
    priorities += ['مراقبة رأس المال العامل والتحصيل بصورة دورية','ربط قرارات الإنفاق بهامش EBITDA والتدفق النقدي الحر','إعادة تقييم السيناريو الضاغط قبل القرارات التمويلية أو التوسعية']
    linkages=executive_linkages(m, bool(cashflow), integrity_unreliable)
    linkage_actions=[x['action'] for x in linkages if x['level'] in {'critical','warning'}]
    priorities=(linkage_actions + priorities)[:4]
    return js({'health_score':score,'classification':label,'analysis_status':status,'narrative':narrative,'strengths':strengths[:3] or ['لا توجد نقطة قوة بارزة وفق الحدود التحليلية الحالية'],'weaknesses':weaknesses[:3] or ['لا توجد نقطة ضعف جوهرية وفق الحدود التحليلية الحالية'],'risks':risks[:3] or ['لا توجد مخاطر حرجة ظاهرة من البيانات المقدمة'],'priorities':priorities,'linkages':linkages,'components':components,'metrics':m,'validation':v})

def scenario_analysis(income,balance,cashflow,changes):
    """Run a management scenario across revenue, cost, working capital and financing."""
    base=canonical(income,balance,cashflow); i=dict(income or {}); b=dict(balance or {}); c=dict(cashflow or {})
    changes=changes or {}
    def adjust(dic,key,pct_change,aliases=()):
        target=key if key in dic else next((a for a in aliases if a in dic),key)
        dic[target]=str(D(dic.get(target,0))*(Decimal('1')+D(pct_change)/HUNDRED))

    revenue_pct=D(changes.get('revenue_pct',0)); cogs_pct=D(changes.get('cogs_pct',0)); opex_pct=D(changes.get('opex_pct',0))
    collection_pct=D(changes.get('collection_pct',0)); financing_pct=D(changes.get('financing_pct', changes.get('debt_pct',0)))
    adjust(i,'revenue',revenue_pct); adjust(i,'cogs',cogs_pct,('cost_of_goods_sold',)); adjust(i,'opex',opex_pct,('operating_expenses',))

    # Financing is modelled as a change to outstanding borrowings. The associated cash movement and
    # incremental interest are carried through the balance sheet, cash-flow statement and income statement.
    debt_base=D(b.get('short_term_debt'))+D(b.get('long_term_debt'))
    financing_delta=debt_base*financing_pct/HUNDRED
    if financing_delta:
        b['long_term_debt']=str(D(b.get('long_term_debt'))+financing_delta)
        b['cash']=str(D(b.get('cash'))+financing_delta)
        base_interest=D(i.get('interest', i.get('interest_expense',0)))
        interest_rate=(base_interest/debt_base) if debt_base else ZERO
        interest_target='interest' if 'interest' in i or 'interest_expense' not in i else 'interest_expense'
        i[interest_target]=str(base_interest+(financing_delta*interest_rate))
        if financing_delta > ZERO:
            c['debt_issued']=str(D(c.get('debt_issued'))+financing_delta)
        else:
            c['debt_repaid']=str(D(c.get('debt_repaid'))+abs(financing_delta))

    collection_delta=ZERO
    if collection_pct and 'accounts_receivable' in b:
        collection_delta=D(b.get('accounts_receivable'))*collection_pct/HUNDRED
        b['accounts_receivable']=str(D(b.get('accounts_receivable'))-collection_delta)
        b['cash']=str(D(b.get('cash'))+collection_delta)
        c['other_operating']=str(D(c.get('other_operating'))+collection_delta)

    # The cash-flow starting point must reflect the scenario's recalculated net income.
    scenario_income_only=canonical(i,b,None)
    if cashflow is not None:
        c['net_income']=str(scenario_income_only['net_income'])
    sc=canonical(i,b,c)
    hb=health_components(base)['score']; hs=health_components(sc)['score']
    keys=['revenue','gross_profit','ebitda','net_income','net_margin','roa','roe','operating_cash_flow','free_cash_flow','ending_cash','current_ratio','debt_to_equity','net_debt_to_ebitda']
    drivers=[]
    driver_specs=[
        ('revenue','الإيرادات',revenue_pct,'نمو/انكماش المبيعات'),
        ('cogs','تكلفة المبيعات',cogs_pct,'تغير تكلفة المبيعات'),
        ('opex','المصاريف التشغيلية',opex_pct,'تغير المصاريف التشغيلية'),
        ('financing','التمويل القائم',financing_pct,'تغير رصيد التمويل'),
        ('collection','التحصيل',collection_pct,'تغير سرعة التحصيل'),
    ]
    for key,label,pct_change,description in driver_specs:
        if pct_change:
            drivers.append({'key':key,'label':label,'change_pct':pct_change,'description':description})

    insights=[]
    net_income_impact=sc['net_income']-base['net_income']
    if net_income_impact >= ZERO:
        insights.append(f"يتحسن صافي الدخل بمقدار {money(net_income_impact)} نتيجة الأثر المجمع لمتغيرات الإيراد والتكلفة والتمويل.")
    else:
        insights.append(f"ينخفض صافي الدخل بمقدار {money(abs(net_income_impact))}؛ ويجب تحديد ما إذا كان السبب تسعيريًا أو تشغيليًا أو تمويليًا قبل اعتماد الخطة.")
    if collection_delta:
        direction='يتحرر' if collection_delta > ZERO else 'يُستهلك'
        insights.append(f"{direction} نقد عامل بمقدار {money(abs(collection_delta))} عبر تغير التحصيل، ما ينعكس على النقد والسيولة قصيرة الأجل.")
    if financing_delta:
        direction='يزداد' if financing_delta > ZERO else 'ينخفض'
        insights.append(f"{direction} التمويل القائم بمقدار {money(abs(financing_delta))}؛ لذلك يتغير النقد المتاح والرفع المالي ومصروف الفائدة معًا.")
    if sc['free_cash_flow'] < ZERO:
        insights.append('يبقى التدفق النقدي الحر سالبًا في السيناريو، ما يستدعي ترتيب الإنفاق الرأسمالي ومصادر تمويله قبل الالتزام بالتوسع.')
    elif sc['free_cash_flow'] >= ZERO and base['free_cash_flow'] < ZERO:
        insights.append('يعبر السيناريو إلى تدفق نقدي حر موجب، ما يحسن القدرة على تمويل النمو أو خفض الالتزامات من الداخل.')

    outlook='يتحسن' if hs>hb else 'يتراجع' if hs<hb else 'لا يتغير جوهريًا'
    executive_summary=(f"{outlook} تقييم الصحة المالية من {hb.quantize(Decimal('.1'))} إلى {hs.quantize(Decimal('.1'))} نقطة. " + ' '.join(insights[:3]))
    assumptions=[
        'تطبّق تغيرات الإيراد والتكلفة والمصاريف على الفترة نفسها دون تغيير في حجم الأصول الثابتة.',
        'يؤثر تغير التمويل في رصيد الدين والنقد ومصروف الفائدة بحسب معدل الفائدة الضمني القائم.',
        'يمثل التحصيل تحريكًا للنقد ورصيد الذمم ولا يغيّر الإيراد المعترف به.',
    ]
    return js({'base':{k:base[k] for k in keys},'scenario':{k:sc[k] for k in keys},'impact':{k:sc[k]-base[k] for k in keys},'health_score':{'base':hb,'scenario':hs,'change':hs-hb},'drivers':drivers,'insights':insights,'executive_summary':executive_summary,'assumptions':assumptions,'financing_delta':financing_delta,'collection_cash_delta':collection_delta})

BENCHMARK_LIBRARY={
    'تجزئة':{
        'source_sector':'Retail (General)','market':'شركات مدرجة أمريكية','as_of':'يناير 2026',
        'source':'Aswath Damodaran — NYU Stern (هوامش القطاع، ROE، Debt Fundamentals)',
        'disclaimer':'مرجع إرشادي لشركات مدرجة أمريكية؛ لا يعادل معيارًا محليًا أو تقييمًا استثماريًا.',
        'benchmark':{
            'net_margin':{'label':'هامش صافي الربح','median':5.61,'lower_quartile':4.49,'upper_quartile':6.73,'unit':'percent','direction':'higher'},
            'roe':{'label':'العائد على حقوق الملكية','median':26.05,'lower_quartile':20.84,'upper_quartile':31.26,'unit':'percent','direction':'higher'},
            'debt_to_ebitda':{'label':'الدين إلى EBITDA','median':1.58,'lower_quartile':1.26,'upper_quartile':1.90,'unit':'multiple','direction':'lower'},
            'interest_coverage':{'label':'تغطية الفائدة','median':18.37,'lower_quartile':14.70,'upper_quartile':22.04,'unit':'multiple','direction':'higher'},
        }
    },
    'تصنيع':{
        'source_sector':'Machinery','market':'شركات مدرجة أمريكية','as_of':'يناير 2026',
        'source':'Aswath Damodaran — NYU Stern (هوامش القطاع، ROE، Debt Fundamentals)',
        'disclaimer':'مرجع إرشادي لشركات مدرجة أمريكية؛ لا يعادل معيارًا محليًا أو تقييمًا استثماريًا.',
        'benchmark':{
            'net_margin':{'label':'هامش صافي الربح','median':10.58,'lower_quartile':8.46,'upper_quartile':12.70,'unit':'percent','direction':'higher'},
            'roe':{'label':'العائد على حقوق الملكية','median':16.42,'lower_quartile':13.14,'upper_quartile':19.70,'unit':'percent','direction':'higher'},
            'debt_to_ebitda':{'label':'الدين إلى EBITDA','median':2.30,'lower_quartile':1.84,'upper_quartile':2.76,'unit':'multiple','direction':'lower'},
            'interest_coverage':{'label':'تغطية الفائدة','median':7.76,'lower_quartile':6.21,'upper_quartile':9.31,'unit':'multiple','direction':'higher'},
        }
    },
    'خدمات':{
        'source_sector':'Business & Consumer Services','market':'شركات مدرجة أمريكية','as_of':'يناير 2026',
        'source':'Aswath Damodaran — NYU Stern (هوامش القطاع، ROE، Debt Fundamentals)',
        'disclaimer':'مرجع إرشادي لشركات مدرجة أمريكية؛ لا يعادل معيارًا محليًا أو تقييمًا استثماريًا.',
        'benchmark':{
            'net_margin':{'label':'هامش صافي الربح','median':7.03,'lower_quartile':5.62,'upper_quartile':8.44,'unit':'percent','direction':'higher'},
            'roe':{'label':'العائد على حقوق الملكية','median':18.20,'lower_quartile':14.56,'upper_quartile':21.84,'unit':'percent','direction':'higher'},
            'debt_to_ebitda':{'label':'الدين إلى EBITDA','median':2.77,'lower_quartile':2.22,'upper_quartile':3.32,'unit':'multiple','direction':'lower'},
            'interest_coverage':{'label':'تغطية الفائدة','median':5.53,'lower_quartile':4.42,'upper_quartile':6.64,'unit':'multiple','direction':'higher'},
        }
    },
    'عقارات':{
        'source_sector':'Real Estate (General/Diversified)','market':'شركات مدرجة أمريكية','as_of':'يناير 2026',
        'source':'Aswath Damodaran — NYU Stern (هوامش القطاع، ROE، Debt Fundamentals)',
        'disclaimer':'مرجع إرشادي لشركات مدرجة أمريكية؛ لا يعادل معيارًا محليًا أو تقييمًا استثماريًا.',
        'benchmark':{
            'net_margin':{'label':'هامش صافي الربح','median':23.77,'lower_quartile':19.02,'upper_quartile':28.52,'unit':'percent','direction':'higher'},
            'roe':{'label':'العائد على حقوق الملكية','median':10.77,'lower_quartile':8.62,'upper_quartile':12.92,'unit':'percent','direction':'higher'},
            'debt_to_ebitda':{'label':'الدين إلى EBITDA','median':9.50,'lower_quartile':7.60,'upper_quartile':11.40,'unit':'multiple','direction':'lower'},
            'interest_coverage':{'label':'تغطية الفائدة','median':5.38,'lower_quartile':4.30,'upper_quartile':6.46,'unit':'multiple','direction':'higher'},
        }
    },
    'مالي':{
        'source_sector':'Financial Services (Non-bank & Insurance)','market':'شركات مدرجة أمريكية','as_of':'يناير 2026',
        'source':'Aswath Damodaran — NYU Stern (هوامش القطاع، ROE، Debt Fundamentals)',
        'disclaimer':'مرجع إرشادي لشركات مدرجة أمريكية؛ تعريفات الرفع المالي للمؤسسات المالية تختلف جوهريًا عن القطاعات التشغيلية.',
        'benchmark':{
            'net_margin':{'label':'هامش صافي الربح','median':22.19,'lower_quartile':17.75,'upper_quartile':26.63,'unit':'percent','direction':'higher'},
            'roe':{'label':'العائد على حقوق الملكية','median':28.82,'lower_quartile':23.06,'upper_quartile':34.58,'unit':'percent','direction':'higher'},
            'debt_to_ebitda':{'label':'الدين إلى EBITDA','median':67.59,'lower_quartile':54.07,'upper_quartile':81.11,'unit':'multiple','direction':'lower'},
            'interest_coverage':{'label':'تغطية الفائدة','median':8.21,'lower_quartile':6.57,'upper_quartile':9.85,'unit':'multiple','direction':'higher'},
        }
    },
}

def sector_benchmark_reference(sector):
    ref=BENCHMARK_LIBRARY.get(str(sector or '').strip())
    if not ref:
        return None
    return js({'sector':sector, **ref})

def benchmark_compare(metrics, benchmark):
    out=[]
    for key,ref in (benchmark or {}).items():
        if key not in metrics: continue
        actual=D(metrics[key]); median=D(ref.get('median')); low=D(ref.get('lower_quartile',median)); high=D(ref.get('upper_quartile',median));
        direction=str(ref.get('direction','higher')).lower()
        if direction == 'lower':
            position='ABOVE' if actual < low else 'BELOW' if actual > high else 'IN_RANGE'
            performance_gap=median-actual
        else:
            position='ABOVE' if actual > high else 'BELOW' if actual < low else 'IN_RANGE'
            performance_gap=actual-median
        performance_gap_pct=pct(performance_gap,abs(median)) if median else ZERO
        out.append({'metric':key,'label':ref.get('label',key),'actual':actual,'median':median,'lower_quartile':low,'upper_quartile':high,'variance':actual-median,'performance_gap':performance_gap,'performance_gap_pct':performance_gap_pct,'direction':direction,'unit':ref.get('unit','number'),'position':position})
    return js(out)
