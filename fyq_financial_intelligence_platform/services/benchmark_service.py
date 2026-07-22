"""
Benchmark Service
"""

from core.decision_intelligence import (
    benchmark_compare,
    sector_benchmark_reference,
    canonical,
    js
)


class BenchmarkService:

    @staticmethod
    def canonical_metrics(
        income,
        balance,
        cashflow
    ):
        return js(
            canonical(
                income,
                balance,
                cashflow
            )
        )

    @staticmethod
    def compare(metrics, benchmark):
        return benchmark_compare(
            metrics,
            benchmark
        )

    @staticmethod
    def reference(sector):
        return sector_benchmark_reference(
            sector
        )
