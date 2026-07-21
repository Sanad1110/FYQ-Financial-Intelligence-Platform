"""
FYQ AUTOMATED TESTING SUITE — جناح الاختبارات الآلي الشامل
═════════════════════════════════════════════════════════════════
Unit Tests | Integration Tests | Validation Tests | Accuracy Tests
"""

import unittest
import sys
from datetime import datetime
from engines import (
    BudgetEngine, ForecastEngine, KPIEngine, VarianceEngine,
    RiskEngine, ConsolidationEngine, DashboardEngine
)
from database import DatabaseManager, UserRole, WorkflowStatus
from rbac import RolePermissions, Permission, AuthorizationManager
from workflow import WorkflowEngine, WorkflowValidator


# ═════════════════════════════════════════════════════════════════
# UNIT TESTS — اختبارات الوحدات
# ═════════════════════════════════════════════════════════════════

class TestBudgetEngine(unittest.TestCase):
    """اختبارات محرك الموازنة"""
    
    def setUp(self):
        self.engine = BudgetEngine()
    
    def test_add_budget_item(self):
        """اختبار إضافة عنصر موازنة"""
        self.engine.add_budget_item('Revenue', 100000, month=1)
        self.assertIn('Revenue', self.engine.budgets)
        self.assertEqual(len(self.engine.budgets['Revenue']), 1)
    
    def test_record_actual(self):
        """اختبار تسجيل المبلغ الفعلي"""
        self.engine.add_budget_item('Revenue', 100000, month=1)
        self.engine.record_actual('Revenue', 105000, month=1)
        
        summary = self.engine.get_budget_summary()
        self.assertEqual(summary['Revenue']['actual'], 105000)
        self.assertEqual(summary['Revenue']['variance'], 5000)
    
    def test_variance_calculation(self):
        """اختبار حساب الانحراف"""
        self.engine.add_budget_item('Expenses', 50000, month=1)
        self.engine.record_actual('Expenses', 48000, month=1)
        
        summary = self.engine.get_budget_summary()
        # للمصاريف، الانحراف السالب مفضل
        self.assertEqual(summary['Expenses']['variance'], -2000)
        self.assertAlmostEqual(summary['Expenses']['variance_pct'], -4.0, places=1)


class TestForecastEngine(unittest.TestCase):
    """اختبارات محرك التنبؤ"""
    
    def setUp(self):
        self.engine = ForecastEngine()
    
    def test_linear_forecast(self):
        """اختبار التنبؤ الخطي"""
        self.engine.add_historical_data('Revenue', [100000, 102000, 104000, 106000])
        forecast = self.engine.forecast_linear('Revenue', periods=3)
        
        self.assertEqual(len(forecast), 3)
        # التنبؤ يجب أن يستمر في الاتجاه الصاعد
        self.assertTrue(all(forecast[i] > forecast[i-1] for i in range(1, len(forecast))))
    
    def test_exponential_smoothing(self):
        """اختبار التمويه الأسي"""
        self.engine.add_historical_data('Revenue', [100000, 102000, 104000, 106000])
        forecast = self.engine.forecast_exponential_smoothing('Revenue', alpha=0.3, periods=3)
        
        self.assertEqual(len(forecast), 3)
        # جميع التنبؤات يجب أن تكون موجبة
        self.assertTrue(all(f > 0 for f in forecast))
    
    def test_forecast_range(self):
        """اختبار نطاق التنبؤ مع فترة ثقة"""
        self.engine.add_historical_data('Revenue', [100000, 102000, 104000, 106000, 108000])
        result = self.engine.get_forecast_range('Revenue', periods=3, confidence=0.95)
        
        self.assertIn('linear_forecast', result)
        self.assertIn('exponential_forecast', result)
        self.assertIn('average_forecast', result)
        self.assertIn('confidence_margin', result)


class TestKPIEngine(unittest.TestCase):
    """اختبارات محرك مؤشرات الأداء"""
    
    def setUp(self):
        self.engine = KPIEngine()
    
    def test_add_kpi(self):
        """اختبار إضافة مؤشر أداء"""
        self.engine.add_kpi('Revenue Growth', 5.2, 6.0, '%', threshold_red=2.0, threshold_yellow=4.0)
        self.assertIn('Revenue Growth', self.engine.kpis)
    
    def test_kpi_status_green(self):
        """اختبار حالة المؤشر الأخضر"""
        self.engine.add_kpi('Margin', 8.0, 10.0, '%', threshold_red=2.0, threshold_yellow=5.0)
        kpi = self.engine.kpis['Margin']
        self.assertEqual(kpi.status, 'GREEN')
    
    def test_kpi_status_yellow(self):
        """اختبار حالة المؤشر الأصفر"""
        self.engine.add_kpi('Margin', 4.5, 10.0, '%', threshold_red=2.0, threshold_yellow=5.0)
        kpi = self.engine.kpis['Margin']
        self.assertEqual(kpi.status, 'YELLOW')
    
    def test_kpi_status_red(self):
        """اختبار حالة المؤشر الأحمر"""
        self.engine.add_kpi('Margin', 1.5, 10.0, '%', threshold_red=2.0, threshold_yellow=5.0)
        kpi = self.engine.kpis['Margin']
        self.assertEqual(kpi.status, 'RED')


class TestVarianceEngine(unittest.TestCase):
    """اختبارات محرك الانحرافات"""
    
    def test_calculate_variances(self):
        """اختبار حساب الانحرافات"""
        budget = {'revenue': 500000, 'expenses': 300000}
        actual = {'revenue': 520000, 'expenses': 295000}
        
        variances = VarianceEngine.calculate_variances(budget, actual)
        
        self.assertEqual(variances['revenue']['absolute_variance'], 20000)
        self.assertEqual(variances['expenses']['absolute_variance'], -5000)
        self.assertAlmostEqual(variances['revenue']['percentage_variance'], 4.0, places=1)
    
    def test_favorable_variance(self):
        """اختبار الانحراف الملائم"""
        budget = {'revenue': 500000}
        actual = {'revenue': 520000}
        
        variances = VarianceEngine.calculate_variances(budget, actual)
        # الإيرادات الزائدة ملائمة
        self.assertTrue(variances['revenue']['favorable'])


class TestRiskEngine(unittest.TestCase):
    """اختبارات محرك المخاطر"""
    
    def setUp(self):
        self.engine = RiskEngine()
    
    def test_add_risk(self):
        """اختبار إضافة مخاطرة"""
        self.engine.add_risk('Market Risk', 0.3, 0.7, 'Diversify portfolio')
        self.assertEqual(len(self.engine.risks), 1)
    
    def test_risk_score_calculation(self):
        """اختبار حساب درجة المخاطرة"""
        self.engine.add_risk('Market Risk', 0.3, 0.7)
        risk = self.engine.risks[0]
        self.assertAlmostEqual(risk.risk_score, 0.21, places=2)
    
    def test_risk_level_classification(self):
        """اختبار تصنيف مستوى المخاطرة"""
        self.engine.add_risk('Critical Risk', 0.9, 0.9)
        self.engine.add_risk('High Risk', 0.6, 0.6)  # 0.36 >= 0.3 = HIGH
        self.engine.add_risk('Low Risk', 0.05, 0.05)
        
        matrix = self.engine.get_risk_matrix()
        self.assertEqual(len(matrix['critical']), 1)
        self.assertEqual(len(matrix['high']), 1)
        self.assertEqual(len(matrix['low']), 1)


# ═════════════════════════════════════════════════════════════════
# INTEGRATION TESTS — اختبارات التكامل
# ═════════════════════════════════════════════════════════════════

class TestDashboardEngine(unittest.TestCase):
    """اختبارات لوحة المعلومات الموحدة"""
    
    def setUp(self):
        self.budget = BudgetEngine()
        self.forecast = ForecastEngine()
        self.kpi = KPIEngine()
        self.risk = RiskEngine()
        self.dashboard = DashboardEngine(self.budget, self.forecast, self.kpi, self.risk)
    
    def test_executive_dashboard(self):
        """اختبار لوحة المعلومات التنفيذية"""
        # إضافة بيانات
        self.budget.add_budget_item('Revenue', 500000, month=1)
        self.budget.record_actual('Revenue', 520000, month=1)
        
        self.kpi.add_kpi('Growth', 5.2, 6.0, '%')
        
        self.risk.add_risk('Market Risk', 0.2, 0.5)
        
        # توليد اللوحة
        dashboard = self.dashboard.generate_executive_dashboard()
        
        self.assertIn('budget_summary', dashboard)
        self.assertIn('kpi_dashboard', dashboard)
        self.assertIn('risk_matrix', dashboard)
        self.assertIn('health_score', dashboard)


# ═════════════════════════════════════════════════════════════════
# RBAC TESTS — اختبارات التحكم في الوصول
# ═════════════════════════════════════════════════════════════════

class TestRBAC(unittest.TestCase):
    """اختبارات نظام التحكم في الوصول"""
    
    def test_admin_permissions(self):
        """اختبار صلاحيات المسؤول"""
        auth = AuthorizationManager(UserRole.ADMIN)
        self.assertTrue(auth.can_perform(Permission.CREATE_USER))
        self.assertTrue(auth.can_perform(Permission.APPROVE_ANALYSIS))
        self.assertTrue(auth.can_perform(Permission.MANAGE_SETTINGS))
    
    def test_analyst_permissions(self):
        """اختبار صلاحيات المحلل"""
        auth = AuthorizationManager(UserRole.ANALYST)
        self.assertTrue(auth.can_perform(Permission.CREATE_ANALYSIS))
        self.assertFalse(auth.can_perform(Permission.APPROVE_ANALYSIS))
        self.assertFalse(auth.can_perform(Permission.MANAGE_SETTINGS))
    
    def test_viewer_permissions(self):
        """اختبار صلاحيات المشاهد"""
        auth = AuthorizationManager(UserRole.VIEWER)
        self.assertFalse(auth.can_perform(Permission.CREATE_ANALYSIS))
        self.assertTrue(auth.can_perform(Permission.READ_ANALYSIS))
        self.assertFalse(auth.can_perform(Permission.APPROVE_ANALYSIS))


# ═════════════════════════════════════════════════════════════════
# WORKFLOW TESTS — اختبارات سير العمل
# ═════════════════════════════════════════════════════════════════

class TestWorkflow(unittest.TestCase):
    """اختبارات سير العمل"""
    
    def setUp(self):
        self.db = DatabaseManager(':memory:')  # قاعدة بيانات في الذاكرة
        self.workflow = WorkflowEngine(self.db)
    
    def test_workflow_transitions(self):
        """اختبار انتقالات سير العمل"""
        # DRAFT → IN_REVIEW
        can_transition = self.workflow.can_transition(
            WorkflowStatus.DRAFT, 
            WorkflowStatus.IN_REVIEW, 
            'analyst'
        )
        self.assertTrue(can_transition)
        
        # DRAFT → APPROVED (غير مسموح)
        can_transition = self.workflow.can_transition(
            WorkflowStatus.DRAFT, 
            WorkflowStatus.APPROVED, 
            'analyst'
        )
        self.assertFalse(can_transition)
    
    def test_approval_permission(self):
        """اختبار صلاحية الموافقة"""
        # المسؤول يمكنه الموافقة
        can_approve = self.workflow.can_transition(
            WorkflowStatus.IN_REVIEW, 
            WorkflowStatus.APPROVED, 
            'finance_manager'
        )
        self.assertTrue(can_approve)
        
        # المحلل لا يمكنه الموافقة
        can_approve = self.workflow.can_transition(
            WorkflowStatus.IN_REVIEW, 
            WorkflowStatus.APPROVED, 
            'analyst'
        )
        self.assertFalse(can_approve)


# ═════════════════════════════════════════════════════════════════
# ACCURACY TESTS — اختبارات الدقة
# ═════════════════════════════════════════════════════════════════

class TestAccuracy(unittest.TestCase):
    """اختبارات دقة الحسابات المالية"""
    
    def test_variance_accuracy(self):
        """اختبار دقة حساب الانحرافات"""
        budget = {'item1': 1000, 'item2': 2000}
        actual = {'item1': 1050, 'item2': 1950}
        
        variances = VarianceEngine.calculate_variances(budget, actual)
        
        # التحقق من الدقة
        self.assertEqual(variances['item1']['absolute_variance'], 50)
        self.assertEqual(variances['item2']['absolute_variance'], -50)
        self.assertAlmostEqual(variances['item1']['percentage_variance'], 5.0, places=1)
        self.assertAlmostEqual(variances['item2']['percentage_variance'], -2.5, places=1)
    
    def test_kpi_achievement_calculation(self):
        """اختبار دقة حساب نسبة التحقق"""
        engine = KPIEngine()
        engine.add_kpi('Target', 75, 100, '%')
        
        kpi = engine.kpis['Target']
        self.assertEqual(kpi.achievement_pct, 75.0)
        self.assertEqual(kpi.gap_to_target, 25)


# ═════════════════════════════════════════════════════════════════
# TEST RUNNER — مشغل الاختبارات
# ═════════════════════════════════════════════════════════════════

def run_all_tests():
    """تشغيل جميع الاختبارات"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # إضافة جميع الاختبارات
    suite.addTests(loader.loadTestsFromTestCase(TestBudgetEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestForecastEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestKPIEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestVarianceEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestDashboardEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestRBAC))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestAccuracy))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # طباعة الملخص
    print("\n" + "="*70)
    print(f"✅ عدد الاختبارات الناجحة: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ عدد الاختبارات الفاشلة: {len(result.failures)}")
    print(f"⚠️  عدد الأخطاء: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
