from flask import Blueprint, request, jsonify

from database import client_store

projects_bp = Blueprint("projects", __name__)


def api_error(message, status=400, exc=None):
    return jsonify({
        "error": message
    }), status


@projects_bp.route('/api/projects', methods=['POST'])
def api_projects_create():

    d = request.get_json(silent=True) or {}

    if not d.get('client_id') or not str(d.get('name', '')).strip():
        return api_error('العميل واسم المشروع مطلوبان.', 400)

    try:
        project_id = client_store.create_project(d)

        return jsonify({
            'id': project_id,
            'status': 'created'
        }), 201

    except Exception as e:
        return api_error(
            'تعذر إنشاء المشروع.',
            400,
            e
        )


@projects_bp.route('/api/projects/<int:pid>/analyses', methods=['GET'])
def api_analyses_list(pid):

    try:
        return jsonify({
            'analyses': client_store.list_analyses(pid)
        })

    except Exception as e:
        return api_error(
            'تعذر جلب تحليلات المشروع.',
            400,
            e
        )


@projects_bp.route('/api/analyses', methods=['POST'])
def api_analysis_save():

    d = request.get_json(silent=True) or {}

    if not d.get('project_id'):
        return api_error('المشروع مطلوب.', 400)

    try:
        analysis_id = client_store.save_analysis(d)

        return jsonify({
            'id': analysis_id,
            'status': 'saved'
        }), 201

    except Exception as e:
        return api_error(
            'تعذر حفظ التحليل.',
            400,
            e
        )


@projects_bp.route('/api/analyses/<int:aid>', methods=['GET'])
def api_analysis_get(aid):

    try:
        analysis = client_store.get_analysis(aid)

        if not analysis:
            return api_error('التحليل غير موجود.', 404)

        return jsonify(analysis)

    except Exception as e:
        return api_error(
            'تعذر استرجاع التحليل.',
            400,
            e
        )
