"""
Scenario Service
"""

from core.decision_intelligence import scenario_analysis


class ScenarioService:

    @staticmethod
    def analyze(
        income,
        balance,
        cashflow,
        changes
    ):
        return scenario_analysis(
            income,
            balance,
            cashflow,
            changes
        )
