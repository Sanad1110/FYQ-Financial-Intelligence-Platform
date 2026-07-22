"""
Valuation Service
"""

from core.valuation_engine import company_valuation


class ValuationService:

    @staticmethod
    def calculate(*args, **kwargs):
        return company_valuation(*args, **kwargs)
