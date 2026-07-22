"""
FP&A Engines Service
"""

from core.engines import (
    BudgetEngine,
    ForecastEngine,
    KPIEngine,
    VarianceEngine,
    RiskEngine,
    ConsolidationEngine,
    DashboardEngine,
)


class EnginesService:

    @staticmethod
    def budget(data):
        return BudgetEngine(data).run()

    @staticmethod
    def forecast(data):
        return ForecastEngine(data).run()

    @staticmethod
    def kpi(data):
        return KPIEngine(data).run()

    @staticmethod
    def variance(data):
        return VarianceEngine(data).run()

    @staticmethod
    def risk(data):
        return RiskEngine(data).run()

    @staticmethod
    def consolidation(data):
        return ConsolidationEngine(data).run()

    @staticmethod
    def dashboard(data):
        return DashboardEngine(data).run()
