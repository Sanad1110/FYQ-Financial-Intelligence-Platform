"""
FYQ ENGINES — محركات الذكاء المالي المتقدمة
═════════════════════════════════════════════════════════════════
Budget Engine | Forecast Engine | KPI Engine | Variance Engine |
Risk Engine | Consolidation Engine | Scenario Engine | Dashboard Engine
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics


# ═════════════════════════════════════════════════════════════════
# BUDGET ENGINE — محرك الموازنة التقديرية
# ═════════════════════════════════════════════════════════════════

@dataclass
class BudgetItem:
    """عنصر في الموازنة التقديرية"""
    category: str          # فئة الموازنة (مثل: الإيرادات، المصاريف)
    budgeted: float        # المبلغ المتوقع
    actual: float = 0.0    # المبلغ الفعلي
    month: int = 1         # الشهر

    @property
    def variance(self) -> float:
        """الانحراف المطلق"""
        return self.actual - self.budgeted

    @property
    def variance_pct(self) -> float:
        """نسبة الانحراف (%)"""
        return (self.variance / self.budgeted * 100) if self.budgeted != 0 else 0

    @property
    def status(self) -> str:
        """حالة الانحراف"""
        if abs(self.variance_pct) <= 5:
            return "ON_TRACK"
        elif self.variance_pct > 5:
            return "OVER"
        else:
            return "UNDER"


class BudgetEngine:
    """محرك الموازنة التقديرية والمراقبة"""
    
    def __init__(self):
        self.budgets: Dict[str, List[BudgetItem]] = {}
    
    def add_budget_item(self, category: str, budgeted: float, month: int = 1):
        """إضافة عنصر موازنة"""
        if category not in self.budgets:
            self.budgets[category] = []
        self.budgets[category].append(BudgetItem(category, budgeted, month=month))
    
    def record_actual(self, category: str, actual: float, month: int = 1):
        """تسجيل المبلغ الفعلي"""
        if category in self.budgets:
            for item in self.budgets[category]:
                if item.month == month:
                    item.actual = actual
                    return
    
    def get_budget_summary(self) -> Dict:
        """الحصول على ملخص الموازنة"""
        summary = {}
        for category, items in self.budgets.items():
            total_budgeted = sum(item.budgeted for item in items)
            total_actual = sum(item.actual for item in items)
            total_variance = total_actual - total_budgeted
            
            summary[category] = {
                'budgeted': total_budgeted,
                'actual': total_actual,
                'variance': total_variance,
                'variance_pct': (total_variance / total_budgeted * 100) if total_budgeted != 0 else 0,
                'items': [
                    {
                        'month': item.month,
                        'budgeted': item.budgeted,
                        'actual': item.actual,
                        'variance': item.variance,
                        'variance_pct': item.variance_pct,
                        'status': item.status
                    }
                    for item in items
                ]
            }
        return summary


# ═════════════════════════════════════════════════════════════════
# FORECAST ENGINE — محرك التنبؤ المالي
# ═════════════════════════════════════════════════════════════════

class ForecastEngine:
    """محرك التنبؤ المالي بناءً على البيانات التاريخية"""
    
    def __init__(self):
        self.historical_data: Dict[str, List[float]] = {}
    
    def add_historical_data(self, metric: str, values: List[float]):
        """إضافة بيانات تاريخية"""
        self.historical_data[metric] = values
    
    def forecast_linear(self, metric: str, periods: int = 3) -> List[float]:
        """التنبؤ باستخدام الاتجاه الخطي (Linear Trend)"""
        if metric not in self.historical_data or len(self.historical_data[metric]) < 2:
            return []
        
        data = self.historical_data[metric]
        n = len(data)
        
        # حساب الانحدار الخطي: y = a + bx
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(data)
        
        numerator = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        b = numerator / denominator if denominator != 0 else 0
        a = y_mean - b * x_mean
        
        # التنبؤ للفترات القادمة
        forecasts = [a + b * (n + i) for i in range(periods)]
        return forecasts
    
    def forecast_exponential_smoothing(self, metric: str, alpha: float = 0.3, periods: int = 3) -> List[float]:
        """التنبؤ باستخدام التمويه الأسي (Exponential Smoothing)"""
        if metric not in self.historical_data or len(self.historical_data[metric]) < 1:
            return []
        
        data = self.historical_data[metric]
        
        # حساب التمويه الأسي
        smoothed = [data[0]]
        for i in range(1, len(data)):
            smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[i - 1])
        
        # التنبؤ
        last_smoothed = smoothed[-1]
        forecasts = [last_smoothed for _ in range(periods)]
        
        return forecasts
    
    def get_forecast_range(self, metric: str, periods: int = 3, confidence: float = 0.95) -> Dict:
        """الحصول على نطاق التنبؤ مع فترة ثقة"""
        linear = self.forecast_linear(metric, periods)
        exponential = self.forecast_exponential_smoothing(metric, periods=periods)
        
        if not linear or not exponential:
            return {}
        
        # حساب الانحراف المعياري من البيانات التاريخية
        if metric in self.historical_data and len(self.historical_data[metric]) > 1:
            std_dev = statistics.stdev(self.historical_data[metric])
        else:
            std_dev = 0
        
        # حساب نطاق الثقة
        z_score = 1.96 if confidence == 0.95 else 2.576  # 95% و 99%
        margin = z_score * std_dev
        
        return {
            'metric': metric,
            'linear_forecast': linear,
            'exponential_forecast': exponential,
            'average_forecast': [(l + e) / 2 for l, e in zip(linear, exponential)],
            'confidence_margin': margin,
            'confidence_level': confidence
        }


# ═════════════════════════════════════════════════════════════════
# VARIANCE ENGINE — محرك تحليل الانحرافات
# ═════════════════════════════════════════════════════════════════

class VarianceEngine:
    """محرك تحليل الانحرافات المتقدم"""
    
    @staticmethod
    def calculate_variances(budget: Dict[str, float], actual: Dict[str, float]) -> Dict:
        """حساب الانحرافات المطلقة والنسبية"""
        variances = {}
        
        for key in budget.keys():
            budgeted = budget.get(key, 0)
            actual_val = actual.get(key, 0)
            
            absolute_variance = actual_val - budgeted
            percentage_variance = (absolute_variance / budgeted * 100) if budgeted != 0 else 0
            
            variances[key] = {
                'budgeted': budgeted,
                'actual': actual_val,
                'absolute_variance': absolute_variance,
                'percentage_variance': percentage_variance,
                'favorable': absolute_variance > 0 if 'revenue' in key.lower() else absolute_variance < 0
            }
        
        return variances
    
    @staticmethod
    def analyze_variance_trends(monthly_variances: List[Dict]) -> Dict:
        """تحليل اتجاهات الانحرافات عبر الأشهر"""
        if not monthly_variances:
            return {}
        
        # استخراج الانحرافات النسبية
        variance_pcts = [v.get('percentage_variance', 0) for v in monthly_variances]
        
        return {
            'average_variance': statistics.mean(variance_pcts),
            'max_variance': max(variance_pcts),
            'min_variance': min(variance_pcts),
            'std_dev': statistics.stdev(variance_pcts) if len(variance_pcts) > 1 else 0,
            'trend': 'improving' if variance_pcts[-1] < statistics.mean(variance_pcts[:-1]) else 'deteriorating'
        }


# ═════════════════════════════════════════════════════════════════
# KPI ENGINE — محرك مؤشرات الأداء الرئيسية
# ═════════════════════════════════════════════════════════════════

@dataclass
class KPI:
    """مؤشر أداء رئيسي"""
    name: str              # اسم المؤشر
    value: float           # القيمة الحالية
    target: float          # الهدف
    unit: str = "%"        # الوحدة
    threshold_red: float = None    # الحد الأحمر
    threshold_yellow: float = None # الحد الأصفر
    
    @property
    def status(self) -> str:
        """حالة المؤشر"""
        if self.threshold_red and self.value <= self.threshold_red:
            return "RED"
        elif self.threshold_yellow and self.value <= self.threshold_yellow:
            return "YELLOW"
        else:
            return "GREEN"
    
    @property
    def achievement_pct(self) -> float:
        """نسبة تحقق الهدف"""
        return (self.value / self.target * 100) if self.target != 0 else 0
    
    @property
    def gap_to_target(self) -> float:
        """الفجوة عن الهدف"""
        return self.target - self.value


class KPIEngine:
    """محرك مؤشرات الأداء الرئيسية"""
    
    def __init__(self):
        self.kpis: Dict[str, KPI] = {}
    
    def add_kpi(self, name: str, value: float, target: float, unit: str = "%", 
                threshold_red: float = None, threshold_yellow: float = None):
        """إضافة مؤشر أداء"""
        self.kpis[name] = KPI(name, value, target, unit, threshold_red, threshold_yellow)
    
    def get_kpi_dashboard(self) -> Dict:
        """الحصول على لوحة مؤشرات الأداء"""
        dashboard = {
            'total_kpis': len(self.kpis),
            'green_count': 0,
            'yellow_count': 0,
            'red_count': 0,
            'kpis': []
        }
        
        for name, kpi in self.kpis.items():
            status = kpi.status
            if status == "GREEN":
                dashboard['green_count'] += 1
            elif status == "YELLOW":
                dashboard['yellow_count'] += 1
            else:
                dashboard['red_count'] += 1
            
            dashboard['kpis'].append({
                'name': name,
                'value': kpi.value,
                'target': kpi.target,
                'unit': kpi.unit,
                'achievement_pct': kpi.achievement_pct,
                'gap_to_target': kpi.gap_to_target,
                'status': status
            })
        
        return dashboard


# ═════════════════════════════════════════════════════════════════
# RISK ENGINE — محرك تحليل المخاطر
# ═════════════════════════════════════════════════════════════════

@dataclass
class Risk:
    """عنصر مخاطرة"""
    name: str
    probability: float     # احتمالية (0-1)
    impact: float         # التأثير (0-1)
    mitigation: str = ""  # التدابير المخففة
    
    @property
    def risk_score(self) -> float:
        """درجة المخاطرة (0-1)"""
        return self.probability * self.impact
    
    @property
    def risk_level(self) -> str:
        """مستوى المخاطرة"""
        score = self.risk_score
        if score >= 0.6:
            return "CRITICAL"
        elif score >= 0.3:
            return "HIGH"
        elif score >= 0.1:
            return "MEDIUM"
        else:
            return "LOW"


class RiskEngine:
    """محرك تحليل المخاطر"""
    
    def __init__(self):
        self.risks: List[Risk] = []
    
    def add_risk(self, name: str, probability: float, impact: float, mitigation: str = ""):
        """إضافة مخاطرة"""
        self.risks.append(Risk(name, probability, impact, mitigation))
    
    def get_risk_matrix(self) -> Dict:
        """الحصول على مصفوفة المخاطر"""
        matrix = {
            'total_risks': len(self.risks),
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'total_risk_score': 0
        }
        
        for risk in self.risks:
            level = risk.risk_level
            risk_data = {
                'name': risk.name,
                'probability': risk.probability,
                'impact': risk.impact,
                'score': risk.risk_score,
                'mitigation': risk.mitigation
            }
            
            if level == "CRITICAL":
                matrix['critical'].append(risk_data)
            elif level == "HIGH":
                matrix['high'].append(risk_data)
            elif level == "MEDIUM":
                matrix['medium'].append(risk_data)
            else:
                matrix['low'].append(risk_data)
            
            matrix['total_risk_score'] += risk.risk_score
        
        return matrix


# ═════════════════════════════════════════════════════════════════
# CONSOLIDATION ENGINE — محرك التجميع والتوحيد
# ═════════════════════════════════════════════════════════════════

class ConsolidationEngine:
    """محرك تجميع البيانات من عدة وحدات/فروع"""
    
    def __init__(self):
        self.entities: Dict[str, Dict] = {}
    
    def add_entity(self, entity_name: str, financial_data: Dict):
        """إضافة وحدة (فرع/شركة تابعة)"""
        self.entities[entity_name] = financial_data
    
    def consolidate(self) -> Dict:
        """تجميع البيانات المالية"""
        if not self.entities:
            return {}
        
        consolidated = {}
        
        # جمع جميع المفاتيح من جميع الوحدات
        all_keys = set()
        for entity_data in self.entities.values():
            all_keys.update(entity_data.keys())
        
        # تجميع القيم
        for key in all_keys:
            total = sum(entity.get(key, 0) for entity in self.entities.values())
            consolidated[key] = total
        
        # إضافة تفاصيل الوحدات
        consolidated['by_entity'] = {
            entity_name: entity_data
            for entity_name, entity_data in self.entities.items()
        }
        
        return consolidated


# ═════════════════════════════════════════════════════════════════
# DASHBOARD ENGINE — محرك لوحة المعلومات الموحدة
# ═════════════════════════════════════════════════════════════════

class DashboardEngine:
    """محرك لوحة المعلومات الموحدة"""
    
    def __init__(self, budget_engine: BudgetEngine, forecast_engine: ForecastEngine,
                 kpi_engine: KPIEngine, risk_engine: RiskEngine):
        self.budget = budget_engine
        self.forecast = forecast_engine
        self.kpi = kpi_engine
        self.risk = risk_engine
    
    def generate_executive_dashboard(self) -> Dict:
        """إنشاء لوحة معلومات تنفيذية موحدة"""
        return {
            'timestamp': datetime.now().isoformat(),
            'budget_summary': self.budget.get_budget_summary(),
            'kpi_dashboard': self.kpi.get_kpi_dashboard(),
            'risk_matrix': self.risk.get_risk_matrix(),
            'health_score': self._calculate_health_score()
        }
    
    def _calculate_health_score(self) -> float:
        """حساب درجة الصحة المالية الكلية"""
        scores = []
        
        # من مؤشرات الأداء
        for kpi in self.kpi.kpis.values():
            scores.append(kpi.achievement_pct / 100)
        
        # من المخاطر
        total_risk = sum(r.risk_score for r in self.risk.risks)
        risk_score = max(0, 1 - (total_risk / len(self.risk.risks))) if self.risk.risks else 1
        scores.append(risk_score)
        
        return (sum(scores) / len(scores) * 100) if scores else 0
