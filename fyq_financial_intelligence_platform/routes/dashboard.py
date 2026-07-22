from flask import Blueprint, request, jsonify

from services.dashboard_service import DashboardService
from utils.api import api_error


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route(
    "/api/dashboard",
    methods=["POST"]
)
def api_dashboard():

    try:

        d = request.get_json(
            silent=True
        ) or {}


        result = DashboardService.analyze(
            d
        )


        return jsonify(
            {
                "status": "ok",
                "dashboard": result,
            }
        )


    except Exception as e:

        return api_error(
            "تعذر معالجة الطلب. تحقق من صحة البيانات المدخلة.",
            400,
            e,
        )
