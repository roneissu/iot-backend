from flask import abort, jsonify, request
from flask_restx import Namespace, Resource, fields
from app.database import db, DeviceType, DeviceAction, DeviceField


api = Namespace('device_type', description='Device Type CRUD')
api_action = Namespace('device_type/action', description='Device Type Action CRUD')
api_field = Namespace('device_type/field', description='Device Type Field CRUD')

device_action_model = api.model('DeviceActionModel', {
    'id': fields.Integer,
    'name': fields.String,
    'action_type': fields.String,
    'device_type': fields.Integer
})

device_field_model = api.model('DeviceFieldModel', {
    'id': fields.Integer,
    'name': fields.String,
    'field_type': fields.String,
    'device_type': fields.Integer
})

device_type_model = api.model('DeviceTypeModel', {
    'name': fields.String,
    'actions': fields.List(fields.Nested(device_action_model)),
    'fields': fields.List(fields.Nested(device_field_model))
})

@api.route('/', methods=["GET", "POST"])
class DeviceTypeView(Resource):
    def get(self):
        device_types = DeviceType.query.all()
        res = []
        for device_type in device_types:
            device_actions, device_fields = DeviceTypeUtils().getActionsFields(device_type.id)
            res.append({
                'id': device_type.id,
                'name': device_type.name,
                'actions': device_actions,
                'fields': device_fields
            })
        return jsonify(res)

    @api.expect(device_type_model)
    def post(self):
        device_type = DeviceType()
        for param in device_type.columns():
            if param != 'id':
                setattr(device_type, param, request.json[param])
        db.session.add(device_type)
        db.session.commit()
        device_actions, device_fields = DeviceTypeUtils().getActionsFields(device_type.id)
        return jsonify({
            'id': device_type.id,
            'name': device_type.name,
            'actions': device_actions,
            'fields': device_fields
        })


@api.route('/<int:id>', methods=["GET", "PATCH", "DELETE"])
class DeviceTypeIdView(Resource):
    def get(self, id):
        device_type = DeviceType.query.filter_by(id=id).first()
        if not device_type:
            abort(404)
        device_actions, device_fields = DeviceTypeUtils().getActionsFields(device_type.id)
        return jsonify({
            'id': device_type.id,
            'name': device_type.name,
            'actions': device_actions,
            'fields': device_fields
        })

    @api.expect(device_type_model)
    def patch(self, id):
        device_type = DeviceType.query.filter_by(id=id).first()
        for param in device_type.columns():
            if param in request.json:
                setattr(device_type, param, request.json[param])
        db.session.add(device_type)
        db.session.commit()
        device_actions, device_fields = DeviceTypeUtils().getActionsFields(device_type.id)
        return jsonify({
            'id': device_type.id,
            'name': device_type.name,
            'actions': device_actions,
            'fields': device_fields
        })

    def delete(self, id):
        device_type = db.session.query(DeviceType).filter(DeviceType.id==id).first()
        db.session.delete(device_type)
        db.session.commit()
        return


@api_action.route('/', methods=["POST"])
class DeviceTypeActionView(Resource):
    @api_action.expect(device_action_model)
    def post(self):
        device_action = DeviceAction()
        for param in device_action.columns():
            if param != 'id':
                setattr(device_action, param, request.json[param])
        db.session.add(device_action)
        db.session.commit()
        return jsonify({
            'id': device_action.id,
            'name': device_action.name,
            'action_type': device_action.action_type,
            'device_type': device_action.device_type
        })


@api_action.route('/<int:id>', methods=["GET", "PATCH", "DELETE"])
class DeviceTypeActionIdView(Resource):
    def get(self, id):
        device_action = DeviceAction.query.filter_by(id=id).first()
        if not device_action:
            abort(404)
        return jsonify({
            'id': device_action.id,
            'name': device_action.name,
            'action_type': device_action.action_type,
            'device_type': device_action.device_type
        })

    @api_action.expect(device_action_model)
    def patch(self, id):
        device_action = DeviceAction.query.filter_by(id=id).first()
        for param in device_action.columns():
            if param in request.json:
                setattr(device_action, param, request.json[param])
        db.session.add(device_action)
        db.session.commit()
        return jsonify({
            'id': device_action.id,
            'name': device_action.name,
            'action_type': device_action.action_type,
            'device_type': device_action.device_type
        })

    def delete(self, id):
        device_action = db.session.query(DeviceAction).filter(DeviceAction.id==id).first()
        db.session.delete(device_action)
        db.session.commit()
        return


@api_field.route('/', methods=["POST"])
class DeviceTypeFieldView(Resource):
    @api_field.expect(device_field_model)
    def post(self):
        device_field = DeviceField()
        for param in device_field.columns():
            if param != 'id':
                setattr(device_field, param, request.json[param])
        db.session.add(device_field)
        db.session.commit()
        return jsonify({
            'id': device_field.id,
            'name': device_field.name,
            'field_type': device_field.field_type,
            'device_type': device_field.device_type
        })


@api_field.route('/<int:id>', methods=["GET", "PATCH", "DELETE"])
class DeviceTypeFieldIdView(Resource):
    def get(self, id):
        device_field = DeviceField.query.filter_by(id=id).first()
        if not device_field:
            abort(404)
        return jsonify({
            'id': device_field.id,
            'name': device_field.name,
            'field_type': device_field.field_type,
            'device_type': device_field.device_type
        })

    @api_field.expect(device_field_model)
    def patch(self, id):
        device_field = DeviceField.query.filter_by(id=id).first()
        for param in device_field.columns():
            if param in request.json:
                setattr(device_field, param, request.json[param])
        db.session.add(device_field)
        db.session.commit()
        return jsonify({
            'id': device_field.id,
            'name': device_field.name,
            'field_type': device_field.field_type,
            'device_type': device_field.device_type
        })

    def delete(self, id):
        device_field = db.session.query(DeviceField).filter(DeviceField.id==id).first()
        db.session.delete(device_field)
        db.session.commit()
        return


class DeviceTypeUtils(Resource):
    def getActionsFields(self, id):
        actions = DeviceAction.query.filter_by(device_type=id).all()
        device_actions = []
        for action in actions:
            device_action = {
                'id': action.id,
                'name': action.name,
                'action_type': action.action_type
            }
            device_actions.append(device_action)
        fields = DeviceField.query.filter_by(device_type=id).all()
        device_fields = []
        for field in fields:
            device_field = {
                'id': field.id,
                'name': field.name,
                'field_type': field.field_type
            }
            device_fields.append(device_field)
        return (device_actions, device_fields)