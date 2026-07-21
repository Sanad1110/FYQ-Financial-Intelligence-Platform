/* ═══════════════════════════════════════════════════════
   FYQ — Financial Decision Intelligence
   ═══════════════════════════════════════════════════════ */

'use strict';

// ─── State ───
const state = {
  income: null,
  balance: null,
  cashflow: null,
  ratios: null,
  advanced: null,
  executive: null,
  charts: {},
  settings: { company: 'شركة نموذجية', year: '2026', currency: 'ريال' }
};

// ─── Chart defaults ───
Chart.defaults.color = '#7a9bbf';
Chart.defaults.font.family = "IBM Plex Sans Arabic, Cairo, sans-serif";
Chart.defaults.font.size = 11;

const COLORS = {
  blue:   '#6c5ce7', cyan:   '#00cec9', gold:   '#fdcb6e',
  green:  '#00b894', red:    '#e17055', purple: '#a29bfe',
  orange: '#e17055', teal:   '#00cec9', pink:   '#fd79a8'
};

// ─── Navigation ───
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    const page = item.dataset.page;
    if (page) navigateTo(page);
  });
});
document.querySelectorAll('.feature-card').forEach(card => {
  card.addEventListener('click', () => {
    const page = card.dataset.page;
    if (page) navigateTo(page);
  });
});

function navigateTo(pageId) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

  const navItem = document.querySelector(`.nav-item[data-page="${pageId}"]`);
  if (navItem) navItem.classList.add('active');

  const page = document.getElementById(`page-${pageId}`);
  if (page) {
    page.classList.add('active');
    page.classList.remove('fade-in');
    void page.offsetWidth;
    page.classList.add('fade-in');
  }

  const titles = {
    home: 'الرئيسية', income: 'قائمة الدخل', balance: 'الميزانية العمومية',
    cashflow: 'التدفقات النقدية', ratios: 'النسب المالية', breakeven: 'نقطة التعادل',
    budget: 'تحليل الموازنة', advanced: 'التحليلات المتقدمة', dashboard: 'لوحة المؤشرات',
    settings: 'الإعدادات', export: 'تصدير التقارير', import: 'استيراد Excel',
    intelligence: 'مركز القرار التنفيذي', clients: 'العملاء والمشاريع',
    scenario: 'السيناريوهات والمحاكاة', benchmark: 'المقارنة القطاعية',
    valuation: 'التقييم المالي', analyses: 'سجل التحليلات',
    about: 'عن FYQ Financial Intelligence Platform'
  };
  document.getElementById('headerPageTitle').textContent = titles[pageId] || pageId;
}

// ─── Helpers ───
function fmt(n, dec = 0) {
  if (n === null || n === undefined || isNaN(n)) return '—';
  return Number(n).toLocaleString('ar-SA', { minimumFractionDigits: dec, maximumFractionDigits: dec });
}
function fmtPct(n) {
  if (n === null || n === undefined || isNaN(n)) return '—';
  return Number(n).toFixed(2) + '%';
}
function val(id) { return parseFloat(document.getElementById(id)?.value) || 0; }
function showLoading() { document.getElementById('loadingOverlay').classList.add('show'); }
function hideLoading() { document.getElementById('loadingOverlay').classList.remove('show'); }
function showToast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast ${type} show`;
  setTimeout(() => t.classList.remove('show'), 3000);
}
function destroyChart(id) {
  if (state.charts[id]) { state.charts[id].destroy(); delete state.charts[id]; }
}
function resultItem(label, value, cls = '') {
  return `<div class="result-item ${cls}"><span class="ri-label">${label}</span><span class="ri-value">${value}</span></div>`;
}
function resultSep() { return '<div class="result-item separator"></div>'; }

// ─── Settings ───
function saveSettings() {
  const company = document.getElementById('set-company').value || 'شركة نموذجية';
  const year    = document.getElementById('set-year').value || '2026';
  const cur     = document.getElementById('set-currency').value || 'ريال';
  // تخزين الإعدادات في state
  state.settings = {
    company,
    year,
    currency: cur,
    sector:   document.getElementById('set-sector')?.value || '',
    cr:       document.getElementById('set-cr')?.value || '',
    preparer: document.getElementById('set-preparer')?.value || '',
    title:    document.getElementById('set-title')?.value || '',
    date:     document.getElementById('set-date')?.value || '',
    notes:    document.getElementById('set-notes')?.value || ''
  };
  document.getElementById('sidebarCompany').textContent = company;
  document.getElementById('sidebarYear').textContent = `${year} — ${cur}`;
  document.getElementById('headerCompany').textContent = company;
  showToast('✅ تم حفظ الإعدادات');
}

// ═══════════════════════════════════════════════════════
// INCOME STATEMENT
// ═══════════════════════════════════════════════════════
function calcIncome() {
  showLoading();
  const data = {
    revenue: val('inc-revenue'), cogs: val('inc-cogs'),
    opex: val('inc-opex'), depreciation: val('inc-dep'),
    interest: val('inc-int'), tax_rate: val('inc-tax')
  };
  fetch('/api/income', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      state.income = res;
      renderIncomeResults(res);
      renderIncomeCharts(res, data);
      renderHomeExecutive();
      showToast('✅ تم حساب قائمة الدخل');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderIncomeResults(r) {
  const d = r.income_statement;
  let html = '';
  html += resultItem('الإيرادات', fmt(d.revenue) + ' ' + getCurrency());
  html += resultItem('تكلفة البضاعة المباعة', '(' + fmt(d.cogs) + ')', 'negative');
  html += resultSep();
  html += resultItem('مجمل الربح', fmt(d.gross_profit) + ' ' + getCurrency(), 'highlight');
  html += resultItem('هامش مجمل الربح', fmtPct(d.gross_margin));
  html += resultSep();
  html += resultItem('المصاريف التشغيلية', '(' + fmt(d.opex) + ')', 'negative');
  html += resultItem('الاستهلاك والإطفاء', '(' + fmt(d.depreciation) + ')', 'negative');
  html += resultSep();
  html += resultItem('EBITDA', fmt(d.ebitda) + ' ' + getCurrency(), 'highlight');
  html += resultItem('EBIT', fmt(d.ebit) + ' ' + getCurrency(), 'highlight');
  html += resultSep();
  html += resultItem('مصاريف الفائدة', '(' + fmt(d.interest) + ')', 'negative');
  html += resultItem('الربح قبل الضريبة', fmt(d.ebt) + ' ' + getCurrency());
  html += resultItem('ضريبة الدخل', '(' + fmt(d.tax || d.tax_amount) + ')', 'negative');
  html += resultSep();
  html += resultItem('صافي الدخل', fmt(d.net_income) + ' ' + getCurrency(), 'total');
  html += resultItem('هامش صافي الدخل', fmtPct(d.net_margin));
  document.getElementById('incomeResultsBody').innerHTML = html;
  document.getElementById('incomeCharts').style.display = 'grid';
}

function renderIncomeCharts(r, data) {
  const d = r.income_statement;
  destroyChart('incomeBarChart');
  destroyChart('incomeMarginChart');

  const ctx1 = document.getElementById('incomeBarChart').getContext('2d');
  state.charts.incomeBarChart = new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: ['الإيرادات', 'التكلفة', 'المصاريف', 'الاستهلاك', 'الفائدة', 'صافي الدخل'],
      datasets: [{
        data: [d.revenue, d.cogs, d.opex, d.depreciation, d.interest, d.net_income],
        backgroundColor: [COLORS.blue, COLORS.red, COLORS.orange, COLORS.purple, COLORS.pink, COLORS.green],
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: { ...chartDefaults(), plugins: { legend: { display: false } } }
  });

  const ctx2 = document.getElementById('incomeMarginChart').getContext('2d');
  state.charts.incomeMarginChart = new Chart(ctx2, {
    type: 'doughnut',
    data: {
      labels: ['هامش مجمل', 'هامش تشغيلي', 'هامش صافي'],
      datasets: [{
        data: [d.gross_margin, d.ebit / d.revenue * 100, d.net_margin],
        backgroundColor: [COLORS.blue, COLORS.gold, COLORS.green],
        borderWidth: 0, hoverOffset: 8
      }]
    },
    options: { ...chartDefaults(), cutout: '65%' }
  });
}

function clearIncome() {
  ['inc-revenue','inc-cogs','inc-opex','inc-dep','inc-int'].forEach(id => {
    document.getElementById(id).value = '';
  });
  document.getElementById('incomeResultsBody').innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted)"><div style="font-size:40px;margin-bottom:12px">📊</div><div>أدخل البيانات واضغط احسب</div></div>';
  document.getElementById('incomeCharts').style.display = 'none';
}

// ═══════════════════════════════════════════════════════
// BALANCE SHEET
// ═══════════════════════════════════════════════════════
function calcBalance() {
  showLoading();
  const data = {
    cash: val('bs-cash'), accounts_receivable: val('bs-ar'),
    inventory: val('bs-inv'), other_current_assets: val('bs-other-ca') || val('bs-oca'),
    fixed_assets: val('bs-ppe') || val('bs-fa'),
    accumulated_depreciation: val('bs-ad') || 0,
    other_long_term_assets: val('bs-other-nca') || val('bs-ola'),
    accounts_payable: val('bs-ap'), short_term_debt: val('bs-std'),
    other_current_liabilities: val('bs-other-cl') || val('bs-ocl'), long_term_debt: val('bs-ltd'),
    other_long_term_liabilities: val('bs-other-ncl') || val('bs-oll'),
    paid_in_capital: val('bs-sc') || val('bs-pic'),
    retained_earnings: val('bs-re')
  };
  fetch('/api/balance', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      state.balance = res;
      renderBalanceResults(res);
      renderHomeExecutive();
      showToast('✅ تم حساب الميزانية العمومية');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderBalanceResults(r) {
  const b = r.balance_sheet;
  const cur = getCurrency();
  let html = `<div class="grid-2">`;
  // Assets
  html += `<div>
    <div style="font-size:11px;color:var(--green);font-weight:700;margin-bottom:8px">الأصول</div>
    ${resultItem('الأصول المتداولة', fmt(b.total_current_assets) + ' ' + cur, 'highlight')}
    ${resultItem('الأصول غير المتداولة', fmt(b.total_non_current_assets) + ' ' + cur, 'highlight')}
    ${resultSep()}
    ${resultItem('إجمالي الأصول', fmt(b.total_assets) + ' ' + cur, 'total')}
  </div>`;
  // Liabilities + Equity
  html += `<div>
    <div style="font-size:11px;color:var(--red);font-weight:700;margin-bottom:8px">الالتزامات وحقوق الملكية</div>
    ${resultItem('الالتزامات المتداولة', fmt(b.total_current_liabilities) + ' ' + cur, 'highlight')}
    ${resultItem('الالتزامات طويلة الأجل', fmt(b.total_non_current_liabilities) + ' ' + cur, 'highlight')}
    ${resultItem('حقوق الملكية', fmt(b.total_equity) + ' ' + cur, 'highlight')}
    ${resultSep()}
    ${resultItem('إجمالي الالتزامات + حقوق الملكية', fmt(b.total_liabilities_equity) + ' ' + cur, 'total')}
  </div>`;
  html += `</div>`;

  const balanced = Math.abs(b.total_assets - b.total_liabilities_equity) < 1;
  html += `<div style="margin-top:12px;padding:12px;border-radius:8px;text-align:center;
    background:${balanced ? 'rgba(0,230,118,0.08)' : 'rgba(255,23,68,0.08)'};
    border:1px solid ${balanced ? 'rgba(0,230,118,0.3)' : 'rgba(255,23,68,0.3)'};
    color:${balanced ? 'var(--green)' : 'var(--red)'};font-weight:700">
    ${balanced ? '✅ الميزانية متوازنة' : '⚠️ الميزانية غير متوازنة — الفرق: ' + fmt(Math.abs(b.total_assets - b.total_liabilities_equity))}
  </div>`;

  document.getElementById('balanceResultsBody').innerHTML = html;
  const charts = document.getElementById('balanceCharts');
  if (charts) charts.style.display = 'block';
  const assets = [b.total_current_assets || 0, b.total_non_current_assets || 0];
  destroyChart('balanceCompositionChart');
  const compositionCanvas = document.getElementById('balanceCompositionChart');
  if (compositionCanvas) {
    state.charts.balanceCompositionChart = new Chart(compositionCanvas.getContext('2d'), {
      type: 'doughnut',
      data: { labels: ['أصول متداولة', 'أصول غير متداولة'], datasets: [{ data: assets, backgroundColor: [COLORS.cyan, COLORS.purple], borderWidth: 0, hoverOffset: 8 }] },
      options: { ...chartDefaults(), cutout: '62%' }
    });
  }
  const funding = [b.total_current_liabilities || 0, b.total_non_current_liabilities || 0, b.total_equity || 0];
  destroyChart('balanceFundingChart');
  const fundingCanvas = document.getElementById('balanceFundingChart');
  if (fundingCanvas) {
    state.charts.balanceFundingChart = new Chart(fundingCanvas.getContext('2d'), {
      type: 'bar',
      data: { labels: ['التزامات متداولة', 'التزامات طويلة', 'حقوق الملكية'], datasets: [{ data: funding, backgroundColor: [COLORS.orange, COLORS.red, COLORS.green], borderRadius: 6, borderSkipped: false }] },
      options: { ...chartDefaults(), plugins: { legend: { display: false } } }
    });
  }
}

function clearBalance() {
  document.getElementById('balanceResultsBody').innerHTML = '<div style="text-align:center;padding:30px;color:var(--text3)"><div style="font-size:32px;margin-bottom:8px">⚖️</div><div style="font-size:11px">أدخل البيانات واضغط احسب</div></div>';
}

// ═══════════════════════════════════════════════════════
// CASH FLOW
// ═══════════════════════════════════════════════════════
function calcCashflow() {
  showLoading();
  const data = {
    net_income: val('cf-ni'), depreciation_add_back: val('cf-dep'),
    change_in_receivables: val('cf-ar-change'), change_in_inventory: val('cf-inv-change'),
    change_in_payables: val('cf-ap-change'),
    other_operating: val('cf-other-op') || val('cf-oo'),
    capex: val('cf-capex'), asset_sales: val('cf-asset-sale') || val('cf-as'),
    other_investing: val('cf-invest') || val('cf-inv'),
    debt_issued: val('cf-new-debt') || val('cf-nd'),
    debt_repaid: val('cf-debt-rep') || val('cf-dr'),
    dividends_paid: val('cf-div'), equity_issued: val('cf-si') || 0,
    other_financing: 0, beginning_cash: val('cf-begin-cash') || 0
  };
  fetch('/api/cashflow', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      state.cashflow = res;
      renderCashflowResults(res);
      renderHomeExecutive();
      showToast('✅ تم حساب التدفقات النقدية');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderCashflowResults(r) {
  const cf = r.cash_flow;
  const cur = getCurrency();
  let html = '';
  html += resultItem('التدفق التشغيلي', fmt(cf.operating_cash_flow) + ' ' + cur, cf.operating_cash_flow >= 0 ? 'positive' : 'negative');
  html += resultItem('التدفق الاستثماري', fmt(cf.investing_cash_flow) + ' ' + cur, cf.investing_cash_flow >= 0 ? 'positive' : 'negative');
  html += resultItem('التدفق التمويلي', fmt(cf.financing_cash_flow) + ' ' + cur, cf.financing_cash_flow >= 0 ? 'positive' : 'negative');
  html += resultSep();
  html += resultItem('صافي التدق النقدي', fmt(cf.net_change_in_cash || cf.net_cash_flow) + ' ' + cur, (cf.net_change_in_cash || cf.net_cash_flow) >= 0 ? 'total positive' : 'total negative');
  html += resultSep();
  html += resultItem('التدفق النقدي الحر (FCF)', fmt(cf.free_cash_flow) + ' ' + cur, cf.free_cash_flow >= 0 ? 'highlight positive' : 'highlight negative');
  document.getElementById('cashflowResultsBody').innerHTML = html;

  // Chart
  destroyChart('cashflowBarChart');
  document.getElementById('cashflowCharts').style.display = 'block';
  const ctx = document.getElementById('cashflowBarChart').getContext('2d');
  const vals = [cf.operating_cash_flow, cf.investing_cash_flow, cf.financing_cash_flow, cf.net_change_in_cash || cf.net_cash_flow || 0];
  state.charts.cashflowBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['تشغيلي', 'استثماري', 'تمويلي', 'صافي'],
      datasets: [{
        data: vals,
        backgroundColor: vals.map(v => v >= 0 ? COLORS.green : COLORS.red),
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: { ...chartDefaults(), plugins: { legend: { display: false } } }
  });
  destroyChart('cashflowDoughnut');
  const donutCanvas = document.getElementById('cashflowDoughnut');
  if (donutCanvas) {
    const mix = [Math.abs(cf.operating_cash_flow || 0), Math.abs(cf.investing_cash_flow || 0), Math.abs(cf.financing_cash_flow || 0)];
    state.charts.cashflowDoughnut = new Chart(donutCanvas.getContext('2d'), {
      type: 'doughnut',
      data: { labels: ['تشغيلي', 'استثماري', 'تمويلي'], datasets: [{ data: mix, backgroundColor: [COLORS.green, COLORS.blue, COLORS.gold], borderWidth: 0, hoverOffset: 8 }] },
      options: { ...chartDefaults(), cutout: '62%' }
    });
  }
}

function clearCashflow() {
  document.getElementById('cashflowResultsBody').innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted)"><div style="font-size:40px;margin-bottom:12px">💧</div><div>أدخل البيانات واضغط احسب</div></div>';
  document.getElementById('cashflowCharts').style.display = 'none';
}

// ═══════════════════════════════════════════════════════
// RATIOS
// ═══════════════════════════════════════════════════════
function calcRatios() {
  if (!state.income || !state.balance) {
    showToast('⚠️ يجب حساب قائمة الدخل والميزانية أولاً', 'error'); return;
  }
  showLoading();
  const data = {
    income: state.income.income_statement,
    balance: state.balance.balance_sheet,
    cashflow: state.cashflow ? state.cashflow.cash_flow : null
  };
  fetch('/api/ratios', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      state.ratios = res;
      renderRatios(res);
      renderHomeExecutive();
      showToast('✅ تم حساب النسب المالية');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderRatios(r) {
  const ra = r.ratios;
  document.getElementById('ratiosContent').style.display = 'block';
  document.getElementById('ratiosEmpty').style.display = 'none';

  // Liquidity
  let liq = '';
  liq += resultItem('النسبة الجارية', fmt(ra.current_ratio, 2) + 'x', ra.current_ratio >= 2 ? 'positive' : ra.current_ratio >= 1 ? '' : 'negative');
  liq += resultItem('النسبة السريعة', fmt(ra.quick_ratio, 2) + 'x', ra.quick_ratio >= 1 ? 'positive' : 'negative');
  liq += resultItem('نسبة النقدية', fmt(ra.cash_ratio, 2) + 'x');
  liq += resultItem('رأس المال العامل', fmt(ra.working_capital));
  document.getElementById('ratiosLiquidity').innerHTML = liq;

  // Profitability
  let prof = '';
  prof += resultItem('هامش مجمل الربح', fmtPct(ra.gross_margin), ra.gross_margin > 30 ? 'positive' : '');
  prof += resultItem('هامش EBITDA', fmtPct(ra.ebitda_margin));
  prof += resultItem('هامش الربح التشغيلي', fmtPct(ra.operating_margin));
  prof += resultItem('هامش صافي الدخل', fmtPct(ra.net_margin), ra.net_margin > 10 ? 'positive' : ra.net_margin > 0 ? '' : 'negative');
  prof += resultItem('ROA', fmtPct(ra.roa), ra.roa > 5 ? 'positive' : '');
  prof += resultItem('ROE', fmtPct(ra.roe), ra.roe > 15 ? 'positive' : '');
  document.getElementById('ratiosProfitability').innerHTML = prof;

  // Efficiency
  let eff = '';
  eff += resultItem('دوران الأصول', fmt(ra.asset_turnover, 2) + 'x');
  eff += resultItem('دوران المخزون', fmt(ra.inventory_turnover, 2) + 'x');
  eff += resultItem('دوران الذمم', fmt(ra.receivables_turnover, 2) + 'x');
  eff += resultItem('أيام التحصيل (DSO)', fmt(ra.days_sales_outstanding, 0) + ' يوم');
  document.getElementById('ratiosEfficiency').innerHTML = eff;

  // Leverage
  let lev = '';
  lev += resultItem('نسبة الدين إلى الأصول', fmt(ra.debt_to_assets, 2), ra.debt_to_assets < 0.5 ? 'positive' : 'negative');
  lev += resultItem('نسبة الدين إلى حقوق الملكية', fmt(ra.debt_to_equity, 2) + 'x');
  lev += resultItem('نسبة تغطية الفائدة', fmt(ra.interest_coverage, 2) + 'x', ra.interest_coverage > 3 ? 'positive' : 'negative');
  lev += resultItem('الرفع المالي', fmt(ra.equity_multiplier, 2) + 'x');
  document.getElementById('ratiosLeverage').innerHTML = lev;

  // Liquidity Chart
  destroyChart('ratiosLiqChart');
  const ctxLiq = document.getElementById('ratiosLiqChart').getContext('2d');
  state.charts.ratiosLiqChart = new Chart(ctxLiq, {
    type: 'bar',
    data: {
      labels: ['التداول', 'السريعة', 'النقدية'],
      datasets: [{
        data: [ra.current_ratio, ra.quick_ratio, ra.cash_ratio],
        backgroundColor: [COLORS.purple, COLORS.cyan, COLORS.teal],
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: { ...chartDefaults(), plugins: { legend: { display: false } } }
  });

  // Profitability Chart
  destroyChart('ratiosProfChart');
  const ctxProf = document.getElementById('ratiosProfChart').getContext('2d');
  state.charts.ratiosProfChart = new Chart(ctxProf, {
    type: 'bar',
    data: {
      labels: ['هامش مجمل الربح', 'هامش الربح التشغيلي', 'هامش صافي الدخل', 'ROA', 'ROE'],
      datasets: [{
        data: [ra.gross_margin, ra.operating_margin, ra.net_margin, ra.roa, ra.roe],
        backgroundColor: [COLORS.green, COLORS.gold, COLORS.cyan, COLORS.purple, COLORS.pink],
        borderRadius: 6, borderSkipped: false
      }]
    },
    options: { ...chartDefaults(), plugins: { legend: { display: false } } }
  });
}

// ═══════════════════════════════════════════════════════
// BREAKEVEN
// ═══════════════════════════════════════════════════════
function calcBreakeven() {
  showLoading();
  const data = {
    fixed_costs: val('be-fc'), variable_cost_per_unit: val('be-vc'),
    selling_price_per_unit: val('be-price'), actual_units: val('be-actual')
  };
  fetch('/api/breakeven', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      renderBreakeven(res, data);
      showToast('✅ تم حساب نقطة التعادل');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderBreakeven(r, data) {
  const b = r.breakeven;
  const cur = getCurrency();
  let html = '';
  html += resultItem('هامش المساهمة للوحدة', fmt(b.contribution_margin) + ' ' + cur);
  html += resultItem('نسبة هامش المساهمة', fmtPct(b.contribution_margin_ratio));
  html += resultSep();
  html += resultItem('نقطة التعادل (وحدات)', fmt(b.breakeven_units, 0) + ' وحدة', 'highlight');
  html += resultItem('نقطة التعادل (مبيعات)', fmt(b.breakeven_revenue) + ' ' + cur, 'highlight');
  html += resultSep();
  html += resultItem('هامش الأمان (وحدات)', fmt(b.margin_of_safety_units, 0) + ' وحدة');
  html += resultItem('هامش الأمان %', fmtPct(b.margin_of_safety_pct), b.margin_of_safety_pct > 20 ? 'positive' : b.margin_of_safety_pct > 0 ? '' : 'negative');
  html += resultItem('الربح الفعلي', fmt(b.profit) + ' ' + cur, b.profit >= 0 ? 'total positive' : 'total negative');
  document.getElementById('breakevenResultsBody').innerHTML = html;

  // Chart
  destroyChart('breakevenChart');
  document.getElementById('breakevenChartCard').style.display = 'block';
  const maxUnits = Math.max(data.actual_units, b.breakeven_units) * 1.3;
  const steps = 20;
  const labels = [];
  const totalCost = [], totalRevenue = [];
  for (let i = 0; i <= steps; i++) {
    const u = (maxUnits / steps) * i;
    labels.push(Math.round(u).toLocaleString('ar-SA'));
    totalCost.push(data.fixed_costs + data.variable_cost_per_unit * u);
    totalRevenue.push(data.selling_price_per_unit * u);
  }
  const ctx = document.getElementById('breakevenChart').getContext('2d');
  state.charts.breakevenChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'الإيرادات', data: totalRevenue, borderColor: COLORS.green, backgroundColor: 'rgba(0,230,118,0.05)', tension: 0.1, pointRadius: 0 },
        { label: 'التكاليف الإجمالية', data: totalCost, borderColor: COLORS.red, backgroundColor: 'rgba(255,23,68,0.05)', tension: 0.1, pointRadius: 0 }
      ]
    },
    options: { ...chartDefaults() }
  });
}

// ═══════════════════════════════════════════════════════
// BUDGET
// ═══════════════════════════════════════════════════════
function calcBudget() {
  showLoading();
  const data = {
    budgeted: { revenue: val('bud-rev-plan'), cogs: val('bud-cost-plan'), opex: 0, net_income: val('bud-profit-plan') },
    actual:   { revenue: val('bud-rev-act'), cogs: val('bud-cost-act'), opex: 0, net_income: val('bud-profit-act') }
  };
  fetch('/api/budget', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      renderBudget(res, data);
      showToast('✅ تم حساب انحرافات الموازنة');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderBudget(r, data) {
  const variances = r.variances;
  const cur = getCurrency();
  let html = '';
  if (Array.isArray(variances)) {
    variances.forEach(vr => {
      if (!vr) return;
      const isPos = vr.favorable;
      html += `<div class="result-item ${isPos ? 'positive' : 'negative'}">
        <span class="ri-label">${vr.label}</span>
        <span class="ri-value">${vr.variance >= 0 ? '+' : ''}${fmt(vr.variance)} (${fmtPct(vr.variance_pct)})</span>
      </div>`;
    });
  }
  document.getElementById('budgetResultsBody').innerHTML = html;
  document.getElementById('budgetChartCard').style.display = 'block';

  // Chart
  destroyChart('budgetBarChart');
  const ctx = document.getElementById('budgetBarChart').getContext('2d');
  const chartLabels = ['الإيرادات', 'التكلفة', 'صافي الدخل'];
  state.charts.budgetBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartLabels,
      datasets: [
        { label: 'المخطط', data: [data.budgeted.revenue, data.budgeted.cogs, data.budgeted.net_income], backgroundColor: COLORS.teal, borderRadius: 4 },
        { label: 'الفعلي', data: [data.actual.revenue, data.actual.cogs, data.actual.net_income], backgroundColor: COLORS.gold, borderRadius: 4 }
      ]
    },
    options: { ...chartDefaults() }
  });
}

// ═══════════════════════════════════════════════════════
// ADVANCED
// ═══════════════════════════════════════════════════════
function calcAdvanced() {
  if (!state.income || !state.balance) {
    showToast('⚠️ يجب حساب قائمة الدخل والميزانية أولاً', 'error'); return;
  }
  showLoading();
  const data = {
    income: state.income.income_statement,
    balance: state.balance.balance_sheet,
    cashflow: state.cashflow ? state.cashflow.cash_flow : null,
    wacc: val('adv-wacc') / 100,
    market_value_equity: val('adv-mve')
  };
  fetch('/api/advanced', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      state.advanced = res;
      renderAdvanced(res);
      renderHomeExecutive();
      showToast('✅ تم حساب التحليلات المتقدمة');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderAdvanced(r) {
  document.getElementById('advancedResults').style.display = 'block';

  // DuPont 3
  const dp = r.dupont_3;
  let dpHtml = `<div class="grid-3" style="text-align:center;margin-bottom:16px">
    <div style="background:rgba(108,92,231,0.08);border:1px solid var(--border);border-radius:8px;padding:14px">
      <div style="font-size:11px;color:var(--text-dim)">هامش الدخل</div>
      <div style="font-size:22px;font-weight:900;color:var(--cyan)">${fmtPct(dp.net_profit_margin)}</div>
    </div>
    <div style="background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.2);border-radius:8px;padding:14px">
      <div style="font-size:11px;color:var(--text-dim)">دوران الأصول</div>
      <div style="font-size:22px;font-weight:900;color:var(--gold)">${fmt(dp.asset_turnover, 2)}x</div>
    </div>
    <div style="background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.2);border-radius:8px;padding:14px">
      <div style="font-size:11px;color:var(--text-dim)">مضاعف حقوق الملكية</div>
      <div style="font-size:22px;font-weight:900;color:var(--green)">${fmt(dp.equity_multiplier, 2)}x</div>
    </div>
  </div>
  <div style="text-align:center;padding:14px;background:rgba(108,92,231,0.08);border:1px solid var(--border);border-radius:8px">
    <div style="font-size:11px;color:var(--text-dim);margin-bottom:4px">ROE (DuPont)</div>
    <div style="font-size:28px;font-weight:900;color:var(--gold)">${fmtPct(dp.roe_dupont)}</div>
  </div>`;
  document.getElementById('dupont3Body').innerHTML = dpHtml;

  // EVA
  const eva = r.eva;
  let evaHtml = '';
  evaHtml += resultItem('NOPAT', fmt(eva.nopat));
  evaHtml += resultItem('رأس المال المستثمر', fmt(eva.invested_capital));
  evaHtml += resultItem('WACC', fmtPct(eva.wacc * 100));
  evaHtml += resultItem('تكلفة رأس المال', fmt(eva.capital_charge));
  evaHtml += resultSep();
  evaHtml += resultItem('EVA', fmt(eva.eva), eva.eva >= 0 ? 'total positive' : 'total negative');
  evaHtml += `<div style="margin-top:10px;padding:10px;border-radius:8px;text-align:center;
    background:${eva.eva >= 0 ? 'rgba(0,230,118,0.08)' : 'rgba(255,23,68,0.08)'};
    border:1px solid ${eva.eva >= 0 ? 'rgba(0,230,118,0.3)' : 'rgba(255,23,68,0.3)'};
    color:${eva.eva >= 0 ? 'var(--green)' : 'var(--red)'};font-size:12px;font-weight:700">
    ${eva.eva >= 0 ? '✅ الشركة تخلق قيمة للمساهمين' : '⚠️ الشركة تدمر قيمة المساهمين'}
  </div>`;
  document.getElementById('evaBody').innerHTML = evaHtml;

  // Altman
  const alt = r.altman;
  let altHtml = '';
  altHtml += resultItem('Z-Score', fmt(alt.z_score, 2), alt.zone === 'safe' ? 'positive' : alt.zone === 'grey' ? '' : 'negative');
  altHtml += `<div class="altman-zone ${alt.zone === 'safe' ? 'altman-safe' : alt.zone === 'grey' ? 'altman-grey' : 'altman-danger'}">
    <span>${alt.zone === 'safe' ? 'المنطقة الآمنة' : alt.zone === 'grey' ? 'المنطقة الرمادية' : 'منطقة التعثر'}</span>
    <span>${alt.zone === 'safe' ? 'Z″ > 2.60' : alt.zone === 'grey' ? '1.10 ≤ Z″ ≤ 2.60' : 'Z″ < 1.10'}</span>
  </div>
  <div class="v6-item" style="margin-top:4px"><small>${alt.thresholds || ''}</small></div>`;
  altHtml += `<div class="v6-item"><b>${alt.model || 'Altman Z″'}</b><br><small>${alt.methodology || ''}</small><br><small>${alt.methodology_note || ''}</small></div>`;
  document.getElementById('altmanBody').innerHTML = altHtml;

  // Scorecard
  const sc = r.scorecard;
  const scoreColor = sc.score >= 80 ? 'var(--green)' : sc.score >= 60 ? 'var(--gold)' : 'var(--red)';
  const scoreCirc = Math.PI * 2 * 52 * (sc.score / 100);
  let scHtml = `<div style="display:flex;align-items:center;gap:20px;margin-bottom:16px">
    <div style="position:relative;width:110px;height:110px;flex-shrink:0">
      <svg width="110" height="110" style="transform:rotate(-90deg)">
        <circle cx="55" cy="55" r="48" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8"/>
        <circle cx="55" cy="55" r="48" fill="none" stroke="${scoreColor}" stroke-width="8"
          stroke-dasharray="${scoreCirc} 1000" stroke-linecap="round"/>
      </svg>
      <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center">
        <div style="font-size:26px;font-weight:900;color:${scoreColor}">${sc.score}</div>
        <div style="font-size:10px;color:var(--text-dim)">/ 100</div>
      </div>
    </div>
    <div>
      <div style="font-size:20px;font-weight:900;color:${scoreColor}">${sc.grade}</div>
      <div style="font-size:13px;color:var(--text-dim)">${sc.label}</div>
    </div>
  </div>`;
  if (sc.details) {
    Object.entries(sc.details).forEach(([k, v]) => {
      const pct = (v.score / v.max) * 100;
      scHtml += `<div class="risk-bar-item">
        <div class="risk-bar-header"><span>${v.label || k}</span><span style="color:var(--gold)">${v.score}/${v.max}</span></div>
        <div class="risk-bar-track"><div class="risk-bar-fill" style="width:${pct}%;background:linear-gradient(90deg,var(--blue),var(--cyan))"></div></div>
      </div>`;
    });
  }
  scHtml += `<div class="v6-item"><b>${sc.methodology_name || 'FYQ Financial Score'}</b><br><small>${sc.methodology_description || 'نموذج تقييم داخلي مملوك.'}</small><br><small>الأوزان: السيولة 20% · الربحية 25% · الكفاءة 20% · المديونية 20% · التدفقات 15%</small></div>`;
  document.getElementById('scorecardBody').innerHTML = scHtml;

  // Risk
  const risk = r.risk;
  let riskHtml = '';
  if (risk && risk.risks) {
    risk.risks.forEach(item => {
      const lvl = item.level === 'low' ? 'risk-low' : item.level === 'medium' ? 'risk-med' : 'risk-high';
      riskHtml += `<div class="risk-bar-item ${lvl}">
        <div class="risk-bar-header">
          <span>${item.name}</span>
          <span style="color:${item.level === 'low' ? 'var(--green)' : item.level === 'medium' ? 'var(--orange)' : 'var(--red)'}">
            ${item.level === 'low' ? 'منخفض' : item.level === 'medium' ? 'متوسط' : 'مرتفع'}
          </span>
        </div>
        <div class="risk-bar-track"><div class="risk-bar-fill" style="width:${item.score}%"></div></div>
      </div>`;
    });
  }
  document.getElementById('riskBody').innerHTML = riskHtml;

  // Recommendations
  const recs = r.recommendations;
  let recsHtml = '';
  if (recs && recs.length) {
    recs.forEach(rec => {
      const cls = rec.type === 'positive' ? 'positive' : rec.type === 'warning' ? 'warning' : 'danger';
      const icon = rec.type === 'positive' ? '✅' : rec.type === 'warning' ? '⚠️' : '🚨';
      recsHtml += `<div class="rec-item ${cls}">
        <span class="rec-icon">${icon}</span>
        <div><div class="rec-title">${rec.title}</div><div class="rec-text">${rec.text}</div></div>
      </div>`;
    });
  }
  document.getElementById('recsBody').innerHTML = recsHtml;
}

// ═══════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════
function buildDashboard() {
  if (!state.income) { showToast('⚠️ يجب حساب قائمة الدخل أولاً', 'error'); return; }
  showLoading();

  const data = {
    income: state.income ? state.income.income_statement : null,
    balance: state.balance ? state.balance.balance_sheet : null,
    cashflow: state.cashflow ? state.cashflow.cash_flow : null,
    ratios: state.ratios ? state.ratios.ratios : null,
    advanced: state.advanced
  };

  fetch('/api/dashboard', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => r.json()).then(res => {
      hideLoading();
      if (res.error) { showToast('❌ ' + res.error, 'error'); return; }
      renderDashboard(res, data);
      renderHomeExecutive();
      showToast('✅ تم تحديث لوحة المؤشرات');
    }).catch(() => { hideLoading(); showToast('❌ خطأ في الاتصال', 'error'); });
}

function renderDashboard(res, data) {
  document.getElementById('dashboardContent').style.display = 'block';
  const companyChip = document.getElementById('dashCompanyChip');
  const yearChip = document.getElementById('dashYearChip');
  const currencyChip = document.getElementById('dashCurrencyChip');
  const systemState = document.getElementById('dashSystemState');
  if (companyChip) companyChip.textContent = state.settings?.company || 'شركة نموذجية';
  if (yearChip) yearChip.textContent = state.settings?.year || '2026';
  if (currencyChip) currencyChip.textContent = getCurrency();
  const fEntity=document.getElementById('fyqEntityFilter'), fYear=document.getElementById('fyqYearFilter'), fSector=document.getElementById('fyqSectorFilter'), fCurrency=document.getElementById('fyqCurrencyFilter');
  if(fEntity) fEntity.textContent=state.settings?.company||'شركة نموذجية';
  if(fYear) fYear.textContent=state.settings?.year||'2026';
  if(fSector) fSector.textContent=state.settings?.sector||'—';
  if(fCurrency) fCurrency.textContent=getCurrency();
  if (systemState) {
    const balanced = res.dashboard?.balance_status?.is_balanced;
    systemState.textContent = balanced === false ? '▲ تنبيه: الميزانية غير متوازنة' : '● البيانات جاهزة والتحقق مكتمل';
    systemState.classList.toggle('warning', balanced === false);
  }
  const emptyEl = document.getElementById('dashboardEmpty');
  if (emptyEl) emptyEl.style.display = 'none';
  const inc = data.income;
  const bal = data.balance;
  const cf  = data.cashflow;
  const cur = getCurrency();

  // KPI Cards
  const kpis = [];
  if (inc) {
    kpis.push({ label: 'الإيرادات', value: formatK(inc.revenue), sub: cur, color: 'blue', icon: '💰' });
    kpis.push({ label: 'مجمل الربح', value: formatK(inc.gross_profit), sub: `هامش ${fmtPct(inc.gross_margin)}`, color: 'gold', icon: '📈' });
    kpis.push({ label: 'EBITDA', value: formatK(inc.ebitda), sub: `هامش ${fmtPct(inc.ebitda / inc.revenue * 100)}`, color: 'teal', icon: '⚡' });
    kpis.push({ label: 'صافي الدخل', value: formatK(inc.net_income), sub: `هامش ${fmtPct(inc.net_margin)}`, color: inc.net_income >= 0 ? 'green' : 'red', icon: '💎' });
  }
  if (bal) {
    kpis.push({ label: 'إجمالي الأصول', value: formatK(bal.total_assets), sub: cur, color: 'purple', icon: '🏛️' });
    kpis.push({ label: 'حقوق الملكية', value: formatK(bal.total_equity), sub: cur, color: 'cyan', icon: '🔑' });
  }
  if (cf) {
    kpis.push({ label: 'التدفق التشغيلي', value: formatK(cf.operating_cash_flow), sub: cur, color: cf.operating_cash_flow >= 0 ? 'green' : 'red', icon: '💧' });
    kpis.push({ label: 'FCF', value: formatK(cf.free_cash_flow), sub: 'التدفق النقدي الحر', color: cf.free_cash_flow >= 0 ? 'teal' : 'red', icon: '🌊' });
  }

  const kpiGrid = document.getElementById('dashKpiGrid');
  kpiGrid.innerHTML = kpis.map(k => `
    <div class="kpi-card ${k.color}">
      <span class="kpi-icon">${k.icon}</span>
      <div class="kpi-label">${k.label}</div>
      <div class="kpi-value">${k.value}</div>
      <div class="kpi-sub">${k.sub}</div>
    </div>
  `).join('');

  // Revenue Chart
  if (inc) {
    destroyChart('dashRevenueChart');
    const ctx1 = document.getElementById('dashRevenueChart').getContext('2d');
    state.charts.dashRevenueChart = new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: ['الإيرادات', 'مجمل الربح', 'EBITDA', 'EBIT', 'صافي الدخل'],
        datasets: [{
          data: [inc.revenue, inc.gross_profit, inc.ebitda, inc.ebit, inc.net_income],
          backgroundColor: [COLORS.blue, COLORS.gold, COLORS.teal, COLORS.cyan, COLORS.green],
          borderRadius: 6, borderSkipped: false
        }]
      },
      options: { ...chartDefaults(), plugins: { legend: { display: false } } }
    });

    // Margins Chart
    destroyChart('dashMarginsChart');
    const ctx2 = document.getElementById('dashMarginsChart').getContext('2d');
    state.charts.dashMarginsChart = new Chart(ctx2, {
      type: 'doughnut',
      data: {
        labels: ['هامش مجمل', 'هامش EBITDA', 'هامش صافي', 'التكاليف'],
        datasets: [{
          data: [
            Math.max(0, inc.gross_margin),
            Math.max(0, inc.ebitda / inc.revenue * 100),
            Math.max(0, inc.net_margin),
            Math.max(0, 100 - inc.gross_margin)
          ],
          backgroundColor: [COLORS.blue, COLORS.gold, COLORS.green, 'rgba(255,255,255,0.05)'],
          borderWidth: 0, hoverOffset: 8
        }]
      },
      options: { ...chartDefaults(), cutout: '60%' }
    });
  }

  // Cashflow Chart
  if (cf) {
    destroyChart('dashCashflowChart');
    const ctx3 = document.getElementById('dashCashflowChart').getContext('2d');
    const cfVals = [cf.operating_cash_flow, cf.investing_cash_flow, cf.financing_cash_flow];
    state.charts.dashCashflowChart = new Chart(ctx3, {
      type: 'bar',
      data: {
        labels: ['تشغيلي', 'استثماري', 'تمويلي'],
        datasets: [{
          data: cfVals,
          backgroundColor: cfVals.map(v => v >= 0 ? COLORS.green : COLORS.red),
          borderRadius: 6, borderSkipped: false
        }]
      },
      options: { ...chartDefaults(), plugins: { legend: { display: false } } }
    });
  }

  // Balance Chart
  if (bal) {
    destroyChart('dashBalanceChart');
    const ctx4 = document.getElementById('dashBalanceChart').getContext('2d');
    state.charts.dashBalanceChart = new Chart(ctx4, {
      type: 'doughnut',
      data: {
        labels: ['الأصول المتداولة', 'الأصول غير المتداولة'],
        datasets: [{
          data: [bal.total_current_assets, bal.total_non_current_assets],
          backgroundColor: [COLORS.blue, COLORS.purple],
          borderWidth: 0, hoverOffset: 8
        }]
      },
      options: { ...chartDefaults(), cutout: '60%' }
    });
  }

  // Score
  if (state.advanced && state.advanced.scorecard) {
    const sc = state.advanced.scorecard;
    const scoreColor = sc.score >= 80 ? 'var(--green)' : sc.score >= 60 ? 'var(--gold)' : 'var(--red)';
    document.getElementById('dashScoreBody').innerHTML = `
      <div style="text-align:center;padding:20px">
        <div style="font-size:56px;font-weight:900;color:${scoreColor}">${sc.score}</div>
        <div style="font-size:14px;color:var(--text-dim)">من 100 — ${sc.grade} ${sc.label}</div>
      </div>`;
  } else {
    document.getElementById('dashScoreBody').innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-muted)">احسب التحليلات المتقدمة أولاً</div>';
  }

  // Risk
  if (state.advanced && state.advanced.risk) {
    const risk = state.advanced.risk;
    let rHtml = '';
    if (risk.risks) {
      risk.risks.slice(0, 4).forEach(item => {
        const lvl = item.level === 'low' ? 'risk-low' : item.level === 'medium' ? 'risk-med' : 'risk-high';
        rHtml += `<div class="risk-bar-item ${lvl}">
          <div class="risk-bar-header"><span>${item.name}</span><span>${item.score}%</span></div>
          <div class="risk-bar-track"><div class="risk-bar-fill" style="width:${item.score}%"></div></div>
        </div>`;
      });
    }
    document.getElementById('dashRiskBody').innerHTML = rHtml;
  } else {
    document.getElementById('dashRiskBody').innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-muted)">احسب التحليلات المتقدمة أولاً</div>';
  }
}

function formatK(n) {
  if (!n && n !== 0) return '—';
  const abs = Math.abs(n);
  const sign = n < 0 ? '-' : '';
  if (abs >= 1e9) return sign + (abs / 1e9).toFixed(1) + 'B';
  if (abs >= 1e6) return sign + (abs / 1e6).toFixed(1) + 'M';
  if (abs >= 1e3) return sign + (abs / 1e3).toFixed(1) + 'K';
  return sign + abs.toFixed(0);
}


// ═══════════════════════════════════════════════════════
// HOME EXECUTIVE SNAPSHOT
// ═══════════════════════════════════════════════════════
function numeric(v) { const n = Number(v); return Number.isFinite(n) ? n : 0; }
function homeHealthData() {
  const executiveScore = numeric(state.executive?.health_score);
  const scorecardScore = numeric(state.advanced?.scorecard?.score);
  const score = executiveScore || scorecardScore;
  if (!score) return { score: null, label: 'قيد استكمال البيانات', color: '#62768a' };
  if (score >= 80) return { score, label: 'قوي', color: COLORS.green };
  if (score >= 60) return { score, label: 'يحتاج متابعة', color: COLORS.gold };
  return { score, label: 'يتطلب إجراء', color: COLORS.red };
}
function homeKpiCard(item) {
  return `<article class="home-kpi-card ${item.tone}"><span>${item.eyebrow}</span><strong>${item.value}</strong><small>${item.label}</small></article>`;
}
function renderHomeExecutive() {
  const empty = document.getElementById('homeExecutiveEmpty');
  const content = document.getElementById('homeExecutiveContent');
  const kpiGrid = document.getElementById('homeKpiGrid');
  const inc = state.income?.income_statement;
  if (!empty || !content || !kpiGrid) return;
  if (!inc) { empty.hidden = false; content.hidden = true; return; }
  empty.hidden = true; content.hidden = false;
  const bal = state.balance?.balance_sheet || {};
  const cf = state.cashflow?.cash_flow || {};
  const ratios = state.ratios?.ratios || {};
  const revenue = numeric(inc.revenue);
  const ebitda = numeric(inc.ebitda);
  const netIncome = numeric(inc.net_income);
  const ebitdaMargin = revenue ? (ebitda / revenue) * 100 : 0;
  const netMargin = revenue ? (netIncome / revenue) * 100 : 0;
  const currentRatio = ratios.current_ratio ?? (numeric(bal.total_current_assets) && numeric(bal.total_current_liabilities) ? numeric(bal.total_current_assets) / numeric(bal.total_current_liabilities) : null);
  const fcf = cf.free_cash_flow;
  const cur = getCurrency();
  const kpis = [
    { eyebrow: 'REVENUE', label: 'الإيرادات', value: `${formatK(revenue)} ${cur}`, tone: 'blue' },
    { eyebrow: 'EBITDA MARGIN', label: 'هامش EBITDA', value: `${fmt(ebitdaMargin, 1)}%`, tone: ebitdaMargin >= 10 ? 'green' : 'gold' },
    { eyebrow: 'NET MARGIN', label: 'هامش صافي الربح', value: `${fmt(netMargin, 1)}%`, tone: netMargin >= 5 ? 'teal' : 'orange' },
    { eyebrow: 'CURRENT RATIO', label: 'السيولة الجارية', value: currentRatio === null ? '—' : `${fmt(currentRatio, 2)}×`, tone: currentRatio === null || currentRatio >= 1.5 ? 'cyan' : 'red' },
    { eyebrow: 'FREE CASH FLOW', label: 'التدفق النقدي الحر', value: fcf === undefined ? '—' : `${formatK(numeric(fcf))} ${cur}`, tone: numeric(fcf) >= 0 ? 'green' : 'red' }
  ];
  kpiGrid.innerHTML = kpis.map(homeKpiCard).join('');

  const health = homeHealthData();
  const scoreValue = document.getElementById('homeHealthGaugeValue');
  const scoreLabel = document.getElementById('homeHealthGaugeLabel');
  const insight = document.getElementById('homeExecutiveInsight');
  if (scoreValue) scoreValue.textContent = health.score === null ? '—' : fmt(health.score, 0);
  if (scoreLabel) scoreLabel.textContent = health.label;
  if (insight) {
    if (state.executive?.narrative) insight.textContent = state.executive.narrative;
    else if (fcf !== undefined && numeric(fcf) < 0) insight.textContent = 'التدفق الحر سالب؛ راقب تمويل الاستثمار والتحصيل قبل توسع الالتزامات.';
    else insight.textContent = 'المؤشرات الأولية جاهزة. شغّل الملخص التنفيذي لتظهر الروابط السببية وأولويات القرار.';
  }
  destroyChart('homeHealthGauge');
  const gauge = document.getElementById('homeHealthGauge');
  if (gauge) {
    const score = health.score === null ? 0 : Math.max(0, Math.min(100, health.score));
    state.charts.homeHealthGauge = new Chart(gauge.getContext('2d'), {
      type: 'doughnut',
      data: { datasets: [{ data: [score, 100 - score], backgroundColor: [health.color, 'rgba(148,163,184,.12)'], borderWidth: 0, borderRadius: 8 }] },
      options: { responsive: true, maintainAspectRatio: false, rotation: -90, circumference: 180, cutout: '78%', plugins: { legend: { display: false }, tooltip: { enabled: false } } }
    });
  }
  destroyChart('homeProfitPulseChart');
  const profitCanvas = document.getElementById('homeProfitPulseChart');
  if (profitCanvas) {
    state.charts.homeProfitPulseChart = new Chart(profitCanvas.getContext('2d'), {
      type: 'bar',
      data: { labels: ['الإيرادات', 'إجمالي الربح', 'EBITDA', 'صافي الدخل'], datasets: [{ data: [revenue, numeric(inc.gross_profit), ebitda, netIncome], backgroundColor: [COLORS.cyan, COLORS.gold, COLORS.teal, netIncome >= 0 ? COLORS.green : COLORS.red], borderRadius: 6, borderSkipped: false }] },
      options: { ...chartDefaults(), plugins: { legend: { display: false } } }
    });
  }
  destroyChart('homeCashPulseChart');
  const cashCanvas = document.getElementById('homeCashPulseChart');
  if (cashCanvas) {
    const cashLabels = cf.operating_cash_flow === undefined ? ['نقدية', 'أصول متداولة', 'التزامات متداولة'] : ['تشغيلي', 'حر', 'نقدية الميزانية'];
    const cashValues = cf.operating_cash_flow === undefined ? [numeric(bal.cash), numeric(bal.total_current_assets), numeric(bal.total_current_liabilities)] : [numeric(cf.operating_cash_flow), numeric(cf.free_cash_flow), numeric(bal.cash)];
    state.charts.homeCashPulseChart = new Chart(cashCanvas.getContext('2d'), {
      type: 'bar',
      data: { labels: cashLabels, datasets: [{ data: cashValues, backgroundColor: cashValues.map(v => v >= 0 ? COLORS.blue : COLORS.red), borderRadius: 6, borderSkipped: false }] },
      options: { ...chartDefaults(), plugins: { legend: { display: false } } }
    });
  }
}

// ═══════════════════════════════════════════════════════
// EXPORT
// ═══════════════════════════════════════════════════════
function exportExcel() {
  if (!state.income) { showToast('⚠️ يجب حساب البيانات أولاً', 'error'); return; }
  showLoading();
  const data = buildExportPayload();
  fetch('/api/export/excel', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => {
      if (!r.ok) return r.json().then(e => { throw new Error(e.error || 'خطأ في التصدير'); });
      return r.blob();
    }).then(blob => {
      hideLoading();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'FYQ_Financial_Report.xlsx'; a.click();
      URL.revokeObjectURL(url);
      showToast('✅ تم تصدير Excel');
    }).catch(e => { hideLoading(); showToast('❌ ' + (e.message || 'خطأ في التصدير'), 'error'); });
}

function exportPPT() {
  if (!state.income) { showToast('⚠️ يجب حساب البيانات أولاً', 'error'); return; }
  showLoading();
  const data = buildExportPayload();
  fetch('/api/export/ppt', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => {
      if (!r.ok) return r.json().then(e => { throw new Error(e.error || 'خطأ في التصدير'); });
      return r.blob();
    }).then(blob => {
      hideLoading();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'FYQ_Executive_Deck.pptx'; a.click();
      URL.revokeObjectURL(url);
      showToast('✅ تم تصدير PowerPoint');
    }).catch(e => { hideLoading(); showToast('❌ ' + (e.message || 'خطأ في التصدير'), 'error'); });
}

function exportPDF() {
  if (!state.income) { showToast('⚠️ يجب حساب البيانات أولاً', 'error'); return; }
  showLoading();
  const data = buildExportPayload();
  fetch('/api/export/pdf', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) })
    .then(r => {
      if (!r.ok) return r.json().then(e => { throw new Error(e.error || 'خطأ في التصدير'); });
      return r.blob();
    }).then(blob => {
      hideLoading();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'FYQ_Executive_Report.pdf'; a.click();
      URL.revokeObjectURL(url);
      showToast('✅ تم تصدير PDF');
    }).catch(e => { hideLoading(); showToast('❌ ' + (e.message || 'خطأ في التصدير'), 'error'); });
}

function buildExportPayload() {
  const s = state.settings || {};
  return {
    company:       s.company  || document.getElementById('set-company')?.value  || 'شركة نموذجية',
    year:          s.year     || document.getElementById('set-year')?.value     || '2026',
    currency:      s.currency || document.getElementById('set-currency')?.value || 'ريال',
    sector:        s.sector   || document.getElementById('set-sector')?.value   || '',
    cr:            s.cr       || document.getElementById('set-cr')?.value       || '',
    preparer:      s.preparer || document.getElementById('set-preparer')?.value || '',
    preparer_title: s.title   || document.getElementById('set-title')?.value   || '',
    report_date:   s.date     || document.getElementById('set-date')?.value     || '',
    notes:         s.notes    || document.getElementById('set-notes')?.value    || '',
    income:   state.income   ? state.income.income_statement   : null,
    balance:  state.balance  ? state.balance.balance_sheet     : null,
    cashflow: state.cashflow ? state.cashflow.cash_flow        : null,
    ratios:   state.ratios   ? state.ratios.ratios             : null,
    advanced: state.advanced
  };
}

// ─── Chart Defaults ───
function chartDefaults() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#7a9bbf', font: { family: 'Tajawal', size: 11 }, padding: 16 }
      },
      tooltip: {
        backgroundColor: 'rgba(6,12,24,0.95)',
        borderColor: 'rgba(108,92,231,0.3)',
        borderWidth: 1,
        titleColor: '#e8f4fd',
        bodyColor: '#7a9bbf',
        padding: 10,
        callbacks: {
          label: ctx => ' ' + ctx.parsed.y?.toLocaleString('ar-SA') || ctx.parsed.toLocaleString('ar-SA')
        }
      }
    },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#7a9bbf' } },
      y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#7a9bbf' } }
    }
  };
}

function getCurrency() {
  return document.getElementById('set-currency')?.value || 'ريال';
}

// ─── Init ───
document.addEventListener('DOMContentLoaded', () => {
  // Set today's date
  const today = new Date().toISOString().split('T')[0];
  const dateEl = document.getElementById('set-date');
  if (dateEl) dateEl.value = today;
});


// ═══════════════════════════════════════════════════════════════
//  IMPORT EXCEL — استيراد بيانات Excel
// ═══════════════════════════════════════════════════════════════

let _importedData = null;

// ─── Drag & Drop Setup ───
document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('importDropzone');
  if (!dropzone) return;

  dropzone.addEventListener('dragover', e => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });
  dropzone.addEventListener('drop', e => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) handleImportFile(file);
  });
  dropzone.addEventListener('click', e => {
    if (e.target.tagName !== 'BUTTON') {
      document.getElementById('importFileInput').click();
    }
  });
});

// ─── Handle File Selection ───
function handleImportFile(file) {
  if (!file) return;

  const ext = file.name.split('.').pop().toLowerCase();
  if (ext !== 'xlsx') {
    showToast('FYQ يدعم ملفات XLSX فقط لضمان قراءة آمنة ودقيقة', 'error');
    return;
  }

  showLoading();

  const formData = new FormData();
  formData.append('file', file);

  fetch('/api/import/excel', {
    method: 'POST',
    body: formData
  })
  .then(r => r.json())
  .then(data => {
    hideLoading();
    if (data.error) {
      showToast('خطأ في الاستيراد: ' + data.error, 'error');
      return;
    }
    _importedData = data;
    renderImportPreview(data, file.name);
    showToast('تم قراءة الملف بنجاح — راجع المعاينة وطبّق البيانات', 'success');
  })
  .catch(err => {
    hideLoading();
    showToast('فشل الاتصال بالخادم: ' + err.message, 'error');
  });
}

// ─── Render Import Preview ───
function renderImportPreview(data, filename) {
  const statusDiv   = document.getElementById('importStatus');
  const previewDiv  = document.getElementById('importPreview');
  const statusBody  = document.getElementById('importStatusContent');
  const previewBody = document.getElementById('importPreviewContent');

  // Status chips
  const sheets = (data.sheets_found || []).join(' · ');
  const confidence = Number(data.confidence_score || 0);
  const warnings = (data.warnings || []).map(w => `<div class="fyq-import-warning">▲ ${w}</div>`).join('');
  statusBody.innerHTML = `
    <div class="import-status-grid">
      <div class="import-status-chip">
        <span class="import-status-chip-icon">📄</span>
        <div>
          <div class="import-status-chip-text">اسم الملف</div>
          <div class="import-status-chip-val" style="font-size:10px;color:var(--cyan)">${filename}</div>
        </div>
      </div>
      <div class="import-status-chip">
        <span class="import-status-chip-icon">📋</span>
        <div>
          <div class="import-status-chip-text">أوراق العمل</div>
          <div class="import-status-chip-val">${(data.sheets_found||[]).length}</div>
        </div>
      </div>
      <div class="import-status-chip">
        <span class="import-status-chip-icon">✅</span>
        <div>
          <div class="import-status-chip-text">حقول مستوردة</div>
          <div class="import-status-chip-val">${data.imported_fields || 0}</div>
        </div>
      </div>
      <div class="import-status-chip ${data.imported_fields < 3 ? 'warning' : ''}">
        <span class="import-status-chip-icon">${data.integrity_status === 'READY' ? '🟢' : '🟡'}</span>
        <div>
          <div class="import-status-chip-text">الحالة</div>
          <div class="import-status-chip-val">${data.integrity_status === 'READY' ? 'جاهز للتطبيق' : 'يحتاج مراجعة'}</div>
        </div>
      </div>
    </div>
    <div style="font-size:10px;color:var(--text3);margin-top:8px">الأوراق: ${sheets}</div>
  `;
  statusBody.innerHTML += `<div class="fyq-import-intel"><div><span>MAPPING CONFIDENCE</span><strong>${confidence.toFixed(1)}%</strong></div><div><span>SELECTED YEAR</span><strong>${data.selected_year || '—'}</strong></div><div><span>MAPPED</span><strong>${data.mapped_fields || 0}</strong></div><div><span>VALIDATED</span><strong>${data.validated_fields || 0}</strong></div><div><span>MISSING CRITICAL</span><strong>${(data.missing_critical||[]).length}</strong></div></div>${warnings}`;
  statusDiv.style.display = 'block';

  // Preview table
  const sections = [
    { key: 'income', title: 'قائمة الدخل', icon: '📊', labels: {
      revenue: 'الإيرادات', cogs: 'تكلفة البضاعة', opex: 'المصاريف التشغيلية',
      depreciation: 'الاستهلاك', interest: 'مصاريف الفائدة', tax_rate: 'معدل الضريبة %'
    }},
    { key: 'balance', title: 'الميزانية العمومية', icon: '⚖️', labels: {
      cash: 'النقدية', accounts_receivable: 'ذمم مدينة', inventory: 'المخزون',
      fixed_assets: 'الأصول الثابتة', accounts_payable: 'ذمم دائنة',
      short_term_debt: 'قروض قصيرة', long_term_debt: 'قروض طويلة',
      paid_in_capital: 'رأس المال', retained_earnings: 'أرباح محتجزة'
    }},
    { key: 'cashflow', title: 'التدفقات النقدية', icon: '💧', labels: {
      net_income: 'صافي الدخل', depreciation_add_back: 'استهلاك مضاف',
      capex: 'نفقات رأسمالية', debt_issued: 'قروض جديدة',
      dividends_paid: 'توزيعات', beginning_cash: 'رصيد بداية'
    }},
  ];

  let html = '';
  sections.forEach(sec => {
    const sdata = data[sec.key] || {};
    if (Object.keys(sdata).length === 0) return;
    html += `
      <div style="margin-bottom:16px">
        <div style="font-size:11px;font-weight:700;color:var(--text2);margin-bottom:6px;padding:4px 8px;background:rgba(255,255,255,0.04);border-radius:4px">
          ${sec.icon} ${sec.title}
        </div>
        <table>
          <thead><tr><th>البيان</th><th>القيمة</th></tr></thead>
          <tbody>
    `;
    Object.entries(sdata).forEach(([k, v]) => {
      const label = sec.labels[k] || k;
      const cls = v >= 0 ? 'val-positive' : 'val-negative';
      html += `<tr><td>${label}</td><td class="${cls}">${Number(v).toLocaleString('ar-SA')}</td></tr>`;
    });
    html += `</tbody></table></div>`;
  });

  if (!html) {
    html = '<div style="text-align:center;padding:20px;color:var(--text3);font-size:11px">لم يتم استيراد أي بيانات — تأكد من استخدام القالب الصحيح</div>';
  }

  previewBody.innerHTML = html;
  previewDiv.style.display = 'block';
}

// ─── Apply Imported Data ───
function applyImportedData() {
  if (!_importedData) {
    showToast('لا توجد بيانات لتطبيقها', 'error');
    return;
  }

  const d = _importedData;
  let applied = 0;

  // قائمة الدخل
  if (d.income) {
    const map = {
      revenue: 'inc-revenue', cogs: 'inc-cogs', opex: 'inc-opex',
      depreciation: 'inc-dep', interest: 'inc-int', tax_rate: 'inc-tax'
    };
    Object.entries(map).forEach(([k, id]) => {
      if (d.income[k] !== undefined) {
        const el = document.getElementById(id);
        if (el) { el.value = d.income[k]; applied++; }
      }
    });
  }

  // الميزانية
  if (d.balance) {
    const map = {
      cash: 'bs-cash', accounts_receivable: 'bs-ar', inventory: 'bs-inv',
      other_current_assets: 'bs-other-ca', fixed_assets: 'bs-ppe',
      accumulated_depreciation: 'bs-ad', other_long_term_assets: 'bs-other-nca',
      accounts_payable: 'bs-ap', short_term_debt: 'bs-std',
      other_current_liabilities: 'bs-other-cl', long_term_debt: 'bs-ltd',
      other_long_term_liabilities: 'bs-other-ncl', paid_in_capital: 'bs-sc',
      retained_earnings: 'bs-re'
    };
    Object.entries(map).forEach(([k, id]) => {
      if (d.balance[k] !== undefined) {
        const el = document.getElementById(id);
        if (el) { el.value = d.balance[k]; applied++; }
      }
    });
  }

  // التدفقات النقدية
  if (d.cashflow) {
    const map = {
      net_income: 'cf-ni', depreciation_add_back: 'cf-dep',
      change_in_receivables: 'cf-ar-change', change_in_inventory: 'cf-inv-change',
      change_in_payables: 'cf-ap-change', other_operating: 'cf-other-op',
      capex: 'cf-capex', asset_sales: 'cf-asset-sale',
      other_investing: 'cf-invest', debt_issued: 'cf-new-debt',
      debt_repaid: 'cf-debt-rep', dividends_paid: 'cf-div', beginning_cash: 'cf-begin-cash'
    };
    Object.entries(map).forEach(([k, id]) => {
      if (d.cashflow[k] !== undefined) {
        const el = document.getElementById(id);
        if (el) { el.value = d.cashflow[k]; applied++; }
      }
    });
  }

  // الإعدادات
  if (d.settings) {
    if (d.settings.company) {
      const el = document.getElementById('set-company');
      if (el) { el.value = d.settings.company; applied++; }
    }
    if (d.settings.year) {
      const el = document.getElementById('set-year');
      if (el) { el.value = d.settings.year; applied++; }
    }
    if (d.settings.currency) {
      const el = document.getElementById('set-currency');
      if (el) {
        const wanted = String(d.settings.currency).trim().toLowerCase();
        for (let i = 0; i < el.options.length; i++) {
          const txt=String(el.options[i].text).trim().toLowerCase(), val=String(el.options[i].value).trim().toLowerCase();
          if (txt === wanted || val === wanted || (wanted.includes('ريال') && (txt.includes('ريال') || val.includes('ريال')))) {
            el.selectedIndex = i; applied++; break;
          }
        }
      }
    }
    if (d.settings.sector) {
      const el=document.getElementById('set-sector');
      if(el){
        const importedSector = String(d.settings.sector).trim();
        const importedKey = importedSector.toLowerCase();
        let matched = false;
        for (let i = 0; i < el.options.length; i++) {
          const optionText = String(el.options[i].text).trim().toLowerCase();
          const optionValue = String(el.options[i].value).trim().toLowerCase();
          if (optionText === importedKey || optionValue === importedKey) {
            el.selectedIndex = i;
            matched = true;
            break;
          }
        }
        if (!matched) {
          const option = document.createElement('option');
          option.value = importedSector;
          option.textContent = importedSector;
          el.appendChild(option);
          el.value = importedSector;
        }
        applied++;
      }
    }
    // Imported metadata is authoritative for this analysis. Persist it immediately
    // so dashboard/export do not fall back to the previous default state.
    saveSettings();
  }

  showToast(`✅ تم تطبيق ${applied} حقلاً — انتقل إلى الصفحات لحساب النتائج`, 'success');

  // إخفاء المعاينة
  document.getElementById('importPreview').style.display = 'none';
  _importedData = null;

  // الانتقال لقائمة الدخل
  setTimeout(() => navigateTo('income'), 1200);
}

// ─── Cancel Import ───
function cancelImport() {
  _importedData = null;
  document.getElementById('importPreview').style.display = 'none';
  document.getElementById('importStatus').style.display = 'none';
  document.getElementById('importFileInput').value = '';
  showToast('تم إلغاء الاستيراد', 'success');
}

// ─── Download Template ───
function downloadTemplate() {
  showLoading();
  fetch('/api/import/template')
    .then(r => {
      if (!r.ok) throw new Error('فشل تحميل القالب');
      return r.blob();
    })
    .then(blob => {
      hideLoading();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'FYQ_Import_Template.xlsx';
      a.click();
      URL.revokeObjectURL(url);
      showToast('تم تحميل القالب بنجاح', 'success');
    })
    .catch(err => {
      hideLoading();
      showToast('خطأ في تحميل القالب: ' + err.message, 'error');
    });
}


// Global client-side safety net
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  hideLoading();
  showToast('❌ تعذر إكمال العملية. تحقق من البيانات ثم أعد المحاولة.', 'error');
});
window.addEventListener('error', (event) => {
  console.error('Client error:', event.error || event.message);
});
window.addEventListener('offline', () => showToast('⚠️ انقطع الاتصال بالشبكة', 'error'));
window.addEventListener('online', () => showToast('✅ عاد الاتصال بالشبكة'));

// ═════════════ FYQ DECISION INTELLIGENCE — DECISION INTELLIGENCE ═════════════
function financialPayload(){
  // Single source of truth for Decision Core payload; preserve cash-flow lineage.
  return {
    income: {revenue:val('inc-revenue'),cogs:val('inc-cogs'),opex:val('inc-opex'),depreciation:val('inc-dep'),interest:val('inc-int'),tax_rate:val('inc-tax')},
    balance: {cash:val('bs-cash'),accounts_receivable:val('bs-ar'),inventory:val('bs-inv'),other_current_assets:val('bs-other-ca'),fixed_assets:val('bs-ppe'),accumulated_depreciation:val('bs-ad'),other_long_term_assets:val('bs-other-nca'),accounts_payable:val('bs-ap'),short_term_debt:val('bs-std'),other_current_liabilities:val('bs-other-cl'),long_term_debt:val('bs-ltd'),other_long_term_liabilities:val('bs-other-ncl'),paid_in_capital:val('bs-sc'),retained_earnings:val('bs-re')},
    cashflow: {net_income:val('cf-ni'),depreciation_add_back:val('cf-dep'),change_in_receivables:val('cf-ar-change'),change_in_inventory:val('cf-inv-change'),change_in_payables:val('cf-ap-change'),other_operating:val('cf-other-op')||val('cf-oo'),capex:val('cf-capex'),asset_sales:val('cf-asset-sale')||val('cf-as'),other_investing:val('cf-invest')||val('cf-inv'),debt_issued:val('cf-new-debt')||val('cf-nd'),debt_repaid:val('cf-debt-rep')||val('cf-dr'),dividends_paid:val('cf-div'),equity_issued:val('cf-si')||0,other_financing:0,beginning_cash:val('cf-begin-cash')||0}
  };
}
async function postV6(url,data){showLoading();try{const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const x=await r.json();if(!r.ok||x.error)throw new Error(x.error||'فشل الطلب');return x}finally{hideLoading()}}
function itemsHtml(arr,cls=''){return (arr||[]).map(x=>`<div class="v6-item ${cls}">${x}</div>`).join('')||'<div class="v6-item">لا توجد ملاحظات</div>'}
async function runValidation(){try{const x=await postV6('/api/validation',financialPayload());document.getElementById('dqScore').textContent=x.score+'/100';document.getElementById('validationState').textContent=x.status;
const hq=document.getElementById('homeQuality'); if(hq) hq.textContent=x.score+'/100';
const hd=document.getElementById('homeDecision'); if(hd) hd.textContent=x.can_analyze?'READY':'BLOCKED';document.getElementById('validationIssues').innerHTML=(x.issues||[]).map(i=>`<div class="v6-item ${i.level.toLowerCase()}"><b>${i.level}</b> — ${i.message}</div>`).join('')||'<div class="v6-item good">✓ البيانات اجتازت الفحص دون ملاحظات</div>';showToast(x.can_analyze?'✅ البيانات جاهزة للتحليل':'⛔ توجد أخطاء حرجة',x.can_analyze?'success':'error')}catch(e){showToast('❌ '+e.message,'error')}}
function escapeHTML(value) { return String(value ?? '').replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch])); }
function executiveLinkageHtml(item) {
  const cls = item.level === 'good' ? 'good' : item.level === 'critical' ? 'critical' : 'warning';
  return `<article class="exec-linkage-card ${cls}"><span>${escapeHTML(item.title)}</span><p><b>السبب:</b> ${escapeHTML(item.cause)}</p><p><b>الأثر:</b> ${escapeHTML(item.effect)}</p><small>${escapeHTML(item.action)}</small></article>`;
}
async function runExecutiveSummary(){try{const x=await postV6('/api/executive-summary',financialPayload());state.executive=x;document.getElementById('execHealth').textContent=(x.health_score==null?'—':x.health_score+'/100');document.getElementById('execClass').textContent=x.classification;
const hh=document.getElementById('homeHealth'); if(hh) hh.textContent=(x.health_score==null?'—':x.health_score+'/100');const hd=document.getElementById('homeDecision'); if(hd) hd.textContent='READY';const vs=document.getElementById('validationState'); if(vs) vs.textContent=x.data_quality_note?'جاهز بملاحظات':'جاهز';document.getElementById('execNarrative').textContent=x.narrative + (x.data_quality_note ? ' تنبيه جودة البيانات: ' + x.data_quality_note : '');document.getElementById('execStrengths').innerHTML=itemsHtml(x.strengths,'good');document.getElementById('execWeaknesses').innerHTML=itemsHtml(x.weaknesses,'warning');document.getElementById('execRisks').innerHTML=itemsHtml(x.risks,'critical');document.getElementById('execPriorities').innerHTML=itemsHtml(x.priorities);const links=document.getElementById('execLinkages');if(links)links.innerHTML=(x.linkages||[]).map(executiveLinkageHtml).join('')||'<div class="exec-linkage-empty">لا تتوفر روابط سببية إضافية من البيانات الحالية.</div>';renderHomeExecutive();showToast('✅ تم بناء الملخص التنفيذي')}catch(e){showToast('❌ '+e.message,'error')}}
function scenarioTone(key, delta) { const lowerIsBetter=['debt_to_equity','net_debt_to_ebitda']; const favourable=lowerIsBetter.includes(key)?delta<=0:delta>=0; return favourable?'good':'critical'; }
function scenarioDisplay(key, value) { const percentage=['net_margin','roa','roe'].includes(key); const multiple=['current_ratio','debt_to_equity','net_debt_to_ebitda'].includes(key); if (percentage) return fmt(value,2)+'%'; if (multiple) return fmt(value,2)+'×'; return fmt(value,0)+(key==='revenue'||key==='gross_profit'||key==='ebitda'||key==='net_income'||key==='operating_cash_flow'||key==='free_cash_flow'||key==='ending_cash'?' '+getCurrency():''); }
function renderScenario(x) {
  const kpis=[['revenue','الإيرادات'],['ebitda','EBITDA'],['net_income','صافي الدخل'],['free_cash_flow','التدفق الحر']];
  const kpi=document.getElementById('scenarioKpiGrid');
  if(kpi) kpi.innerHTML=kpis.map(([key,label])=>{const delta=numeric(x.impact[key]);return `<div class="scenario-kpi ${scenarioTone(key,delta)}"><span>${label}</span><strong>${scenarioDisplay(key,x.scenario[key])}</strong><small>${delta>=0?'+':''}${scenarioDisplay(key,delta)} مقابل الأساس</small></div>`}).join('');
  const readout=document.getElementById('scenarioExecutiveReadout'); if(readout) readout.innerHTML=`<b>القراءة التنفيذية</b><p>${escapeHTML(x.executive_summary || '')}</p>`;
  const keys={revenue:'الإيرادات',ebitda:'EBITDA',net_income:'صافي الدخل',net_margin:'هامش صافي الدخل',roa:'ROA',roe:'ROE',operating_cash_flow:'التدفق التشغيلي',free_cash_flow:'التدفق الحر',ending_cash:'النقد الختامي',current_ratio:'نسبة التداول',debt_to_equity:'الدين/حقوق الملكية',net_debt_to_ebitda:'صافي الدين/EBITDA'};
  const result=document.getElementById('scenarioResults');
  if(result) result.innerHTML=(x.insights||[]).map(i=>`<div class="v6-item">${escapeHTML(i)}</div>`).join('')+(x.drivers||[]).length?((x.insights||[]).map(i=>`<div class="v6-item">${escapeHTML(i)}</div>`).join('')+`<div class="scenario-drivers">${(x.drivers||[]).map(d=>`<span>${escapeHTML(d.label)}: ${numeric(d.change_pct)>=0?'+':''}${fmt(d.change_pct,1)}%</span>`).join('')}</div>`):Object.entries(keys).map(([key,label])=>`<div class="v6-item ${scenarioTone(key,numeric(x.impact[key]))}"><b>${label}</b> — ${scenarioDisplay(key,x.base[key])} ← ${scenarioDisplay(key,x.scenario[key])}</div>`).join('');
  destroyChart('scenarioPerformanceChart'); const performance=document.getElementById('scenarioPerformanceChart'); if(performance){state.charts.scenarioPerformanceChart=new Chart(performance.getContext('2d'),{type:'bar',data:{labels:['الإيرادات','EBITDA','صافي الدخل','التدفق الحر'],datasets:[{label:'الأساس',data:['revenue','ebitda','net_income','free_cash_flow'].map(k=>numeric(x.base[k])),backgroundColor:'rgba(121,231,255,.35)',borderRadius:6},{label:'السيناريو',data:['revenue','ebitda','net_income','free_cash_flow'].map(k=>numeric(x.scenario[k])),backgroundColor:COLORS.cyan,borderRadius:6}]},options:{...chartDefaults()}})}
  destroyChart('scenarioRatioChart'); const ratios=document.getElementById('scenarioRatioChart'); if(ratios){state.charts.scenarioRatioChart=new Chart(ratios.getContext('2d'),{type:'bar',data:{labels:['هامش صافي','ROA','ROE'],datasets:[{label:'الأساس',data:['net_margin','roa','roe'].map(k=>numeric(x.base[k])),backgroundColor:'rgba(255,202,98,.38)',borderRadius:6},{label:'السيناريو',data:['net_margin','roa','roe'].map(k=>numeric(x.scenario[k])),backgroundColor:COLORS.gold,borderRadius:6}]},options:{...chartDefaults()}})}
}
async function runScenario(){try{const p=financialPayload();p.changes={revenue_pct:val('sc-revenue'),cogs_pct:val('sc-cogs'),opex_pct:val('sc-opex'),financing_pct:val('sc-financing'),collection_pct:val('sc-collection')};const x=await postV6('/api/scenario',p);renderScenario(x)}catch(e){showToast('❌ '+e.message,'error')}}
const BENCHMARK_UI_META={
  'تجزئة':'Retail (General) · هامش صافي، ROE، الدين إلى EBITDA وتغطية الفائدة',
  'تصنيع':'Machinery · هامش صافي، ROE، الدين إلى EBITDA وتغطية الفائدة',
  'خدمات':'Business & Consumer Services · هامش صافي، ROE، الدين إلى EBITDA وتغطية الفائدة',
  'عقارات':'Real Estate (General/Diversified) · هامش صافي، ROE، الدين إلى EBITDA وتغطية الفائدة',
  'مالي':'Financial Services · تُفسّر مؤشرات الرفع المالي بحذر وفق طبيعة القطاع'
};
function syncBenchmarkSector(){const note=document.getElementById('benchmarkReferenceNote');const sector=document.getElementById('bm-sector')?.value||'';if(note)note.innerHTML=`<b>مرجع FYQ الإرشادي</b><span>${escapeHTML(BENCHMARK_UI_META[sector]||'')}</span><small>Damodaran / NYU Stern · يناير 2026 · نطاق شركات مدرجة أمريكية.</small>`;}
function toggleBenchmarkMode(){const mode=document.getElementById('bm-mode')?.value||'industry';const custom=document.getElementById('bm-custom-fields');if(custom)custom.style.display=mode==='custom'?'block':'none';syncBenchmarkSector();}
function benchmarkDisplay(item,value){if(item.unit==='percent')return fmt(value,2)+'%';if(item.unit==='multiple')return fmt(value,2)+'×';return fmt(value,2);}
function benchmarkClass(position){return position==='ABOVE'?'good':position==='BELOW'?'critical':'warning';}
function renderBenchmark(x){const comparison=x.comparison||[];const meta=document.getElementById('benchmarkMeta');if(meta){const ref=x.reference||{};meta.innerHTML=`<b>${escapeHTML(x.sector||'مرجع المقارنة')}</b><span>${escapeHTML(ref.source_sector||x.market||'')}</span><small>${escapeHTML(x.source||'')} · ${escapeHTML(ref.as_of||'مرجع مخصص')}</small>${ref.disclaimer?`<em>${escapeHTML(ref.disclaimer)}</em>`:''}`;}
 const cards=document.getElementById('benchmarkKpiGrid');if(cards)cards.innerHTML=comparison.map(i=>`<div class="benchmark-kpi ${benchmarkClass(i.position)}"><span>${escapeHTML(i.label||i.metric)}</span><strong>${benchmarkDisplay(i,i.actual)}</strong><small>المرجع ${benchmarkDisplay(i,i.median)} · ${i.position==='ABOVE'?'أفضل من النطاق':i.position==='BELOW'?'دون النطاق':'ضمن النطاق'}</small></div>`).join('');
 const readout=document.getElementById('benchmarkExecutiveReadout');if(readout)readout.innerHTML=`<b>القراءة التنفيذية</b><p>${escapeHTML(x.summary||'')}</p>`;
 const results=document.getElementById('benchmarkResults');if(results)results.innerHTML=comparison.map(i=>`<div class="v6-item ${benchmarkClass(i.position)}"><b>${escapeHTML(i.label||i.metric)}</b> — الفعلي ${benchmarkDisplay(i,i.actual)} مقابل المرجع ${benchmarkDisplay(i,i.median)}. <small>${i.position==='ABOVE'?'فجوة أداء إيجابية':i.position==='BELOW'?'فجوة تحتاج معالجة':'ضمن النطاق المرجعي'}${i.direction==='lower'?'؛ الأقل أفضل في هذا المؤشر.':''}</small></div>`).join('')||'<div class="v6-item">لا توجد مؤشرات قابلة للمقارنة من البيانات الحالية.</div>';
 const labels=comparison.map(i=>i.label||i.metric);const index=comparison.map(i=>{const a=numeric(i.actual),m=numeric(i.median);if(!m)return 0;return i.direction==='lower'?(a?m/a:200):(a/m)*100;});const gaps=comparison.map(i=>numeric(i.performance_gap_pct));
 destroyChart('benchmarkPerformanceChart');const perf=document.getElementById('benchmarkPerformanceChart');if(perf){state.charts.benchmarkPerformanceChart=new Chart(perf.getContext('2d'),{type:'bar',data:{labels,datasets:[{label:'مؤشر الأداء (100 = المرجع)',data:index,backgroundColor:index.map(v=>v>=100?COLORS.green:COLORS.red),borderRadius:6}]},options:{...chartDefaults(),plugins:{...chartDefaults().plugins,legend:{display:false}}}})}
 destroyChart('benchmarkGapChart');const gap=document.getElementById('benchmarkGapChart');if(gap){state.charts.benchmarkGapChart=new Chart(gap.getContext('2d'),{type:'bar',data:{labels,datasets:[{label:'فجوة الأداء الملائمة %',data:gaps,backgroundColor:gaps.map(v=>v>=0?COLORS.cyan:COLORS.orange),borderRadius:6}]},options:{...chartDefaults(),plugins:{...chartDefaults().plugins,legend:{display:false}}}})}
}
async function runBenchmark(){try{const mode=document.getElementById('bm-mode')?.value||'industry';const p=financialPayload();p.sector=document.getElementById('bm-sector').value;p.market=document.getElementById('bm-market')?.value||'';p.source=document.getElementById('bm-source')?.value||'مرجع يحدده المستخدم';p.use_industry_reference=mode==='industry';if(mode==='custom'){const mk=(m)=>({median:m,lower_quartile:m*.75,upper_quartile:m*1.25});p.benchmark={net_margin:{...mk(val('bm-nm')),label:'هامش صافي الربح',unit:'percent',direction:'higher'},roa:{...mk(val('bm-roa')),label:'ROA',unit:'percent',direction:'higher'},roe:{...mk(val('bm-roe')),label:'ROE',unit:'percent',direction:'higher'},current_ratio:{...mk(val('bm-cr')),label:'نسبة التداول',unit:'multiple',direction:'higher'}};}const x=await postV6('/api/benchmark',p);renderBenchmark(x)}catch(e){showToast('❌ '+e.message,'error')}}
document.addEventListener('DOMContentLoaded',()=>{toggleBenchmarkMode();});
async function loadClients(){try{const x=await fetch('/api/clients').then(r=>r.json());document.getElementById('clientsList').innerHTML=(x.clients||[]).map(c=>`<div class="client-card" onclick="selectClient(${c.id},'${String(c.name).replace(/'/g,"\\'")}')"><b>${c.name}</b><br><small>${c.sector||'بدون قطاع'} · ${c.cr_number||'—'}</small></div>`).join('')||'لا يوجد عملاء بعد.'}catch(e){}}
async function createClient(){try{await postV6('/api/clients',{name:document.getElementById('client-name').value,sector:document.getElementById('client-sector').value,cr_number:document.getElementById('client-cr').value});showToast('✅ تمت إضافة العميل');loadClients()}catch(e){showToast('❌ '+e.message,'error')}}
async function selectClient(id,name){const x=await fetch(`/api/clients/${id}/projects`).then(r=>r.json());document.getElementById('projectsArea').innerHTML=`<div class="v6-commandbar"><b>${name}</b><input id="new-project-name" placeholder="اسم المشروع"><input id="new-project-year" placeholder="السنة"><button class="btn btn-primary btn-sm" onclick="createProject(${id},'${String(name).replace(/'/g,"\\'")}')">مشروع جديد</button></div>`+(x.projects||[]).map(p=>`<div class="v6-item"><b>${p.name}</b> — ${p.fiscal_year||'—'} <button class="btn btn-primary btn-sm" onclick="saveCurrentAnalysis(${p.id})">حفظ التحليل الحالي</button></div>`).join('')}
async function createProject(clientId,name){try{await postV6('/api/projects',{client_id:clientId,name:document.getElementById('new-project-name').value,fiscal_year:document.getElementById('new-project-year').value,currency:getCurrency()});selectClient(clientId,name)}catch(e){showToast('❌ '+e.message,'error')}}
async function saveCurrentAnalysis(projectId){try{await postV6('/api/analyses',{project_id:projectId,payload:financialPayload()});showToast('✅ تم حفظ التحليل في سجل المشروع')}catch(e){showToast('❌ '+e.message,'error')}}
document.addEventListener('DOMContentLoaded',loadClients);


// ═════════════ FYQ ADVANCED FEATURES — VALUATION & RESTORATION ═════════════
async function runValuation(){try{const p=financialPayload();p.valuation={wacc:val('val-wacc')/100,terminal_growth:val('val-terminal-growth')/100,forecast_years:val('val-forecast-years'),revenue_growth:val('val-revenue-growth')/100,pe_multiple:val('val-pe-multiple'),ps_multiple:val('val-ps-multiple')};const x=await postV6('/api/valuation',p);const dcf_range=`${fmt(x.dcf_low,0)} - ${fmt(x.dcf_high,0)}`;const pe_val=fmt(x.pe_valuation,0);const ps_val=fmt(x.ps_valuation,0);const avg_val=fmt(x.average_valuation,0);document.getElementById('valuationResults').innerHTML=`<div class="v6-item"><b>تقييم التدفقات المخصومة (DCF)</b><br><small>النطاق: ${dcf_range}</small><br><strong style="color:var(--cyan)">${fmt(x.dcf_midpoint,0)}</strong></div><div class="v6-item"><b>تقييم مضاعف الربح (P/E)</b><br><small>بناءً على صافي الدخل</small><br><strong style="color:var(--gold)">${pe_val}</strong></div><div class="v6-item"><b>تقييم مضاعف الإيرادات (P/S)</b><br><small>بناءً على الإيرادات الكلية</small><br><strong style="color:var(--green)">${ps_val}</strong></div><div class="v6-item" style="background:rgba(108,92,231,0.1);border-left:3px solid var(--blue)"><b>متوسط التقييم</b><br><strong style="color:var(--blue);font-size:16px">${avg_val}</strong><br><small>متوسط الطرق الثلاث</small></div><div class="v6-item"><b>معدل الخصم (WACC)</b>: ${fmt(x.wacc*100,2)}%<br><b>معدل النمو الدائم</b>: ${fmt(x.terminal_growth*100,2)}%</div>`}catch(e){showToast('❌ '+e.message,'error')}}
async function loadAllAnalyses(){try{const clients=await fetch('/api/clients').then(r=>r.json());let html='';for(const c of (clients.clients||[])){const projects=await fetch(`/api/clients/${c.id}/projects`).then(r=>r.json());for(const p of (projects.projects||[])){const analyses=await fetch(`/api/projects/${p.id}/analyses`).then(r=>r.json());for(const a of (analyses.analyses||[])){html+=`<div class="v6-item" style="cursor:pointer;transition:all 0.2s" onmouseover="this.style.background='rgba(108,92,231,0.1)'" onmouseout="this.style.background='transparent'" onclick="restoreAnalysis('${a.id}','${String(c.name).replace(/'/g,"\\'")}','${String(p.name).replace(/'/g,"\\'")}')" ><b>${c.name}</b> / ${p.name}<br><small>التاريخ: ${new Date(a.created_at).toLocaleDateString('ar-SA')} | الحالة: ${a.status||'محفوظ'}</small></div>`}}}document.getElementById('analysesList').innerHTML=html||'<div class="v6-item">لا توجد تحليلات محفوظة بعد.</div>'}catch(e){showToast('❌ خطأ في تحميل التحليلات: '+e.message,'error')}}
async function restoreAnalysis(analysisId,clientName,projectName){try{showLoading();const x=await fetch(`/api/analyses/${analysisId}`).then(r=>r.json());if(!x.payload)throw new Error('بيانات التحليل غير متوفرة');const p=x.payload;if(p.income)Object.entries(p.income).forEach(([k,v])=>{const el=document.getElementById(`inc-${k.replace(/_/g,'-')}`);if(el)el.value=v});if(p.balance)Object.entries(p.balance).forEach(([k,v])=>{const el=document.getElementById(`bs-${k.replace(/_/g,'-')}`);if(el)el.value=v});if(p.cashflow)Object.entries(p.cashflow).forEach(([k,v])=>{const el=document.getElementById(`cf-${k.replace(/_/g,'-')}`);if(el)el.value=v});hideLoading();navigateTo('income');showToast(`✅ تم استعادة التحليل: ${clientName} / ${projectName}`,'success')}catch(e){hideLoading();showToast('❌ '+e.message,'error')}}
async function saveAnalysisWithNotes(){try{const notes=prompt('أضف ملاحظات على هذا التحليل (اختياري):','');const p=financialPayload();p.notes=notes||'';p.saved_at=new Date().toISOString();await postV6('/api/analyses',{project_id:state.currentProjectId,payload:p,notes:notes});showToast('✅ تم حفظ التحليل مع الملاحظات','success');loadAllAnalyses()}catch(e){showToast('❌ '+e.message,'error')}}
document.addEventListener('DOMContentLoaded',()=>{loadClients();loadAllAnalyses()});
