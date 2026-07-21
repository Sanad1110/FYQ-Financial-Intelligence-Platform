from flask import Blueprint, request, jsonify

clients_bp = Blueprint("clients", __name__)


@clients_bp.route('/api/clients', methods=['GET','POST'])
def api_clients():
    from app import client_store, api_error

    if request.method == 'GET':
        return jsonify({'clients': client_store.list_clients()})

    d = request.get_json(silent=True) or {}

    if not str(d.get('name','')).strip():
        return api_error('اسم العميل مطلوب.',400)

    return jsonify({
        'id': client_store.create_client(d),
        'status':'created'
    }),201


@clients_bp.route('/api/clients/<int:cid>', methods=['DELETE'])
def api_client_delete(cid):
    from app import client_store

    client_store.delete_client(cid)

    return jsonify({'status':'deleted'})


@clients_bp.route('/api/clients/<int:cid>/projects', methods=['GET'])
def api_projects_list(cid):
    from app import client_store

    return jsonify({
        'projects': client_store.list_projects(cid)
    })
