from flask import Blueprint, request, jsonify

projects_bp = Blueprint("projects", __name__)


@projects_bp.route('/api/projects', methods=['POST'])
def api_projects_create():
    from app import client_store, api_error

    d = request.get_json(silent=True) or {}

    if not d.get('client_id') or not str(d.get('name','')).strip():
        return api_error('العميل واسم المشروع مطلوبان.',400)

    return jsonify({
        'id': client_store.create_project(d),
        'status':'created'
    }),201


@projects_bp.route('/api/projects/<int:pid>/analyses', methods=['GET'])
def api_analyses_list(pid):
    from app import client_store

    return jsonify({
        'analyses': client_store.list_analyses(pid)
    })


@projects_bp.route('/api/analyses', methods=['POST'])
def api_analysis_save():
    from app import client_store, api_error

    d = request.get_json(silent=True) or {}

    if not d.get('project_id'):
        return api_error('المشروع مطلوب.',400)

    return jsonify({
        'id': client_store.save_analysis(d),
        'status':'saved'
    }),201


@projects_bp.route('/api/analyses/<int:aid>', methods=['GET'])
def api_analysis_get(aid):
    from app import client_store, api_error

    try:
        analysis = client_store.get_analysis(aid)

        if not analysis:
            return api_error('التحليل غير موجود.',404)

        return jsonify(analysis)

    except Exception as e:
        return api_error('تعذر استرجاع التحليل.',400,e)
