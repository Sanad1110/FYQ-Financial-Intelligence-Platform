from flask import Blueprint, request, send_file
import io

from exporters.exporters_wrapper import (
    ExcelExporter,
    PPTExporter,
    PDFExporter,
)
from utils.api import api_error

import_export_bp = Blueprint("import_export", __name__)


@import_export_bp.route("/api/export/excel", methods=["POST"])
def api_export_excel():
    try:
        d = request.get_json(silent=True) or {}

        exp = ExcelExporter(d)

        buf = io.BytesIO()
        exp.export(buf)
        buf.seek(0)

        return send_file(
            buf,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="FYQ_Financial_Report.xlsx",
        )

    except Exception as e:
        return api_error(
            "تعذر تصدير ملف Excel.",
            400,
            e,
        )


@import_export_bp.route("/api/export/ppt", methods=["POST"])
def api_export_ppt():
    try:
        d = request.get_json(silent=True) or {}

        exp = PPTExporter(d)

        buf = io.BytesIO()
        exp.export(buf)
        buf.seek(0)

        return send_file(
            buf,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name="FYQ_Executive_Deck.pptx",
        )

    except Exception as e:
        return api_error(
            "تعذر تصدير ملف PowerPoint.",
            400,
            e,
        )


@import_export_bp.route("/api/export/pdf", methods=["POST"])
def api_export_pdf():
    try:
        d = request.get_json(silent=True) or {}

        exp = PDFExporter(d)

        buf = io.BytesIO()
        exp.export(buf)
        buf.seek(0)

        return send_file(
            buf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="FYQ_Executive_Report.pdf",
        )

    except Exception as e:
        return api_error(
            "تعذر تصدير ملف PDF.",
            400,
            e,
        )
