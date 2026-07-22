from flask import Blueprint, request, jsonify

from services.benchmark_service import BenchmarkService
from utils.api import api_error


benchmark_bp = Blueprint(
    "benchmark",
    __name__
)


@benchmark_bp.route(
    "/api/benchmark",
    methods=["POST"]
)
def api_benchmark():

    try:

        d = request.get_json(
            silent=True
        ) or {}


        metrics = BenchmarkService.build_metrics(
            d.get("income") or {},
            d.get("balance") or {},
            d.get("cashflow") or {},
        )


        use_industry = bool(
            d.get("use_industry_reference")
        )


        reference = None


        if use_industry:

            reference = BenchmarkService.reference(
                d.get("sector", "")
            )


            if not reference:
                return jsonify({
                    "error":
                    "لا يتوفر مرجع قطاعي مدمج للصناعة المختارة."
                }), 400


            benchmark = reference.get(
                "benchmark",
                {}
            )

            source = reference.get(
                "source"
            )

            market = reference.get(
                "market"
            )


        else:

            benchmark = d.get(
                "benchmark"
            ) or {}

            source = d.get(
                "source",
                "مرجع يحدده المستخدم"
            )

            market = d.get(
                "market",
                ""
            )


        comparison = BenchmarkService.compare(
            metrics,
            benchmark
        )


        return jsonify({
            "comparison": comparison,
            "source": source,
            "market": market,
            "reference": reference,
        })


    except Exception as e:

        return api_error(
            "تعذر إنشاء المقارنة المرجعية.",
            400,
            e
        )
