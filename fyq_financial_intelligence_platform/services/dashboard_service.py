"""
Dashboard Service
"""

from core.dashboard_engine import build_dashboard


class DashboardService:

    @staticmethod
    def generate(*args, **kwargs):
        return build_dashboard(*args, **kwargs)
