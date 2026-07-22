"""
FYQ FP&A Engines Service
Enterprise Adapter Layer
"""

from core.engines import (
    BudgetEngine,
    ForecastEngine,
    KPIEngine,
    VarianceEngine,
    RiskEngine,
    ConsolidationEngine,
)


class EnginesService:


    @staticmethod
    def budget(data):

        engine = BudgetEngine()

        for item in data.get("budgets", []):

            engine.add_budget_item(
                category=item.get("category",""),
                budgeted=float(item.get("budgeted",0)),
                month=int(item.get("month",1))
            )

            engine.record_actual(
                category=item.get("category",""),
                actual=float(item.get("actual",0)),
                month=int(item.get("month",1))
            )

        return engine.get_budget_summary()



    @staticmethod
    def forecast(data):

        engine = ForecastEngine()

        for metric, values in data.get("historical",{}).items():

            engine.add_historical_data(
                metric,
                values
            )

        result={}

        for metric in engine.historical_data:

            result[metric]=engine.get_forecast_range(
                metric
            )

        return result



    @staticmethod
    def kpi(data):

        engine = KPIEngine()

        for item in data.get("kpis",[]):

            engine.add_kpi(
                name=item.get("name",""),
                value=float(item.get("value",0)),
                target=float(item.get("target",0)),
                unit=item.get("unit","%"),
            )

        return engine.get_kpi_dashboard()



    @staticmethod
    def variance(data):

        engine = VarianceEngine()

        return engine.get_variance_report()



    @staticmethod
    def risk(data):

        engine = RiskEngine()

        for item in data.get("risks",[]):

            engine.add_risk(
                name=item.get("name",""),
                probability=float(item.get("probability",0)),
                impact=float(item.get("impact",0)),
                mitigation=item.get("mitigation","")
            )

        return engine.get_risk_matrix()



    @staticmethod
    def consolidation(data):

        engine = ConsolidationEngine()

        for name, values in data.get("entities",{}).items():

            engine.add_entity(
                name,
                values
            )

        return engine.consolidate()



    @staticmethod
    def dashboard(data):

        return {

            "status":"ready",

            "budget":
                EnginesService.budget(data),

            "kpi":
                EnginesService.kpi(data),

            "risk":
                EnginesService.risk(data),

            "forecast":
                EnginesService.forecast(data)

        }
