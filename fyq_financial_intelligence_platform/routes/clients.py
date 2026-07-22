from flask import Blueprint, request, jsonify

from database import client_store

clients_bp = Blueprint("clients", __name__)


def api_error(message, status=400):
    return jsonify({
        "error": message
    }), status


@clients_bp.route('/api/clients', methods=['GET', 'POST'])
def api_clients():

    if request.method == 'GET':
        return jsonify({
            'clients': client_store.list_clients()
        })

    d = request.get_json(silent=True) or {}

    name = str(d.get('name', '')).strip()

    if not name:
        return api_error('اسم العميل مطلوب.', 400)

    client_id = client_store.create_client(d)

    return jsonify({
        'id': client_id,
        'status': 'created'
    }), 201


@clients_bp.route('/api/clients/<int:cid>', methods=['DELETE'])
def api_client_delete(cid):

    try:
        client_store.delete_client(cid)

        return jsonify({
            'status': 'deleted'
        })

    except Exception as e:
        return api_error(
            f'تعذر حذف العميل: {str(e)}',
            400
        )


@clients_bp.route('/api/clients/<int:cid>/projects', methods=['GET'])
def api_projects_list(cid):

    try:
        return jsonify({
            'projects': client_store.list_projects(cid)
        })

    except Exception as e:
        return api_error(
            f'تعذر جلب مشاريع العميل: {str(e)}',
            400
        )
