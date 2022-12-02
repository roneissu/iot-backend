# pyright: reportOptionalSubscript=false
from flask import abort, jsonify, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.database import (DeviceAction, DeviceActionParam, DeviceField,
                          DeviceType, db)
from app.device import DeviceUtils

api = Namespace("device_type", description="Device Type CRUD")
api_action_param = Namespace(
    "device_type/action/param", description="Device Type Action Param CRUD"
)
api_action = Namespace("device_type/action", description="Device Type Action CRUD")
api_field = Namespace("device_type/field", description="Device Type Field CRUD")

device_action_param_model = api.model(
    "DeviceActionParamModel",
    {
        "id": fields.Integer,
        "name": fields.String,
        "param_type": fields.String,
        "action": fields.Integer,
    },
)

device_action_model = api.model(
    "DeviceActionModel",
    {
        "id": fields.Integer,
        "name": fields.String,
        "function": fields.String,
        "params": fields.List(fields.Nested(device_action_param_model)),
        "device_type": fields.Integer,
    },
)

device_field_model = api.model(
    "DeviceFieldModel",
    {
        "id": fields.Integer,
        "name": fields.String,
        "unit": fields.String,
        "field_type": fields.String,
        "device_type": fields.Integer,
    },
)

device_type_model = api.model(
    "DeviceTypeModel",
    {
        "name": fields.String,
        "actions": fields.List(fields.Nested(device_action_model)),
        "fields": fields.List(fields.Nested(device_field_model)),
    },
)


@api.route("/", methods=["GET", "POST"])
class DeviceTypeView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    def get(self):
        device_types = DeviceType.query.all()
        res = []
        for device_type in device_types:
            device_actions, device_fields = DeviceTypeUtils().getActionsFields(
                device_type.id
            )
            res.append(
                {
                    "id": device_type.id,
                    "name": device_type.name,
                    "actions": device_actions,
                    "fields": device_fields,
                }
            )
        return jsonify(res)

    @api.expect(device_type_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def post(self):
        device_type = DeviceType()
        for param in device_type.columns():
            if param != "id":
                setattr(device_type, param, request.json[param])
        db.session.add(device_type)
        db.session.commit()
        device_actions, device_fields = DeviceTypeUtils().getActionsFields(
            device_type.id
        )
        return jsonify(
            {
                "id": device_type.id,
                "name": device_type.name,
                "actions": device_actions,
                "fields": device_fields,
            }
        )


@api.route("/<int:id>", methods=["GET", "PATCH", "DELETE"])
class DeviceTypeIdView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    def get(self, id):
        device_type = DeviceType.query.filter_by(id=id).first()
        if not device_type:
            abort(404)
        device_actions, device_fields = DeviceTypeUtils().getActionsFields(
            device_type.id
        )
        return jsonify(
            {
                "id": device_type.id,
                "name": device_type.name,
                "actions": device_actions,
                "fields": device_fields,
            }
        )

    @api.expect(device_type_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def patch(self, id):
        device_type = DeviceType.query.filter_by(id=id).first()
        for param in device_type.columns():
            if param in request.json:
                setattr(device_type, param, request.json[param])
        db.session.add(device_type)
        db.session.commit()
        device_actions, device_fields = DeviceTypeUtils().getActionsFields(
            device_type.id
        )
        return jsonify(
            {
                "id": device_type.id,
                "name": device_type.name,
                "actions": device_actions,
                "fields": device_fields,
            }
        )

    @api.doc(security="Bearer")
    @jwt_required()
    def delete(self, id):
        device_type = db.session.query(DeviceType).filter(DeviceType.id == id).first()
        db.session.delete(device_type)
        db.session.commit()
        return


@api_action.route("/", methods=["POST"])
class DeviceTypeActionView(Resource):
    @api_action.expect(device_action_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def post(self):
        device_action = DeviceAction()
        for param in device_action.columns():
            if param != "id":
                setattr(device_action, param, request.json[param])
        db.session.add(device_action)
        db.session.commit()
        action_params = DeviceTypeUtils().getActionParamsFields(device_action.id)
        return jsonify(
            {
                "id": device_action.id,
                "name": device_action.name,
                "function": device_action.function,
                "device_type": device_action.device_type,
                "params": action_params,
            }
        )


@api_action.route("/<int:id>", methods=["GET", "PATCH", "DELETE"])
class DeviceTypeActionIdView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    def get(self, id):
        device_action = DeviceAction.query.filter_by(id=id).first()
        if not device_action:
            abort(404)
        action_params = DeviceTypeUtils().getActionParamsFields(device_action.id)
        return jsonify(
            {
                "id": device_action.id,
                "name": device_action.name,
                "function": device_action.function,
                "device_type": device_action.device_type,
                "params": action_params,
            }
        )

    @api_action.expect(device_action_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def patch(self, id):
        device_action = DeviceAction.query.filter_by(id=id).first()
        for param in device_action.columns():
            if param in request.json:
                setattr(device_action, param, request.json[param])
        db.session.add(device_action)
        db.session.commit()
        action_params = DeviceTypeUtils().getActionParamsFields(device_action.id)
        return jsonify(
            {
                "id": device_action.id,
                "name": device_action.name,
                "function": device_action.function,
                "device_type": device_action.device_type,
                "params": action_params,
            }
        )

    @api.doc(security="Bearer")
    @jwt_required()
    def delete(self, id):
        device_action = (
            db.session.query(DeviceAction).filter(DeviceAction.id == id).first()
        )
        db.session.delete(device_action)
        db.session.commit()
        return


@api_action_param.route("/", methods=["POST"])
class DeviceTypeActionParamView(Resource):
    @api_action_param.expect(device_action_param_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def post(self):
        action_param = DeviceActionParam()
        for param in action_param.columns():
            if param != "id":
                setattr(action_param, param, request.json[param])
        db.session.add(action_param)
        db.session.commit()
        return jsonify(
            {
                "id": action_param.id,
                "name": action_param.name,
                "param_type": action_param.param_type,
                "action": action_param.action,
            }
        )


@api_action_param.route("/<int:id>", methods=["GET", "PATCH", "DELETE"])
class DeviceTypeActionParamIdView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    def get(self, id):
        action_param = DeviceActionParam.query.filter_by(id=id).first()
        if not action_param:
            abort(404)
        return jsonify(
            {
                "id": action_param.id,
                "name": action_param.name,
                "param_type": action_param.param_type,
                "action": action_param.action,
            }
        )

    @api_action_param.expect(device_action_param_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def patch(self, id):
        action_param = DeviceActionParam.query.filter_by(id=id).first()
        for param in action_param.columns():
            if param in request.json:
                setattr(action_param, param, request.json[param])
        db.session.add(action_param)
        db.session.commit()
        return jsonify(
            {
                "id": action_param.id,
                "name": action_param.name,
                "param_type": action_param.param_type,
                "action": action_param.action,
            }
        )

    @api.doc(security="Bearer")
    @jwt_required()
    def delete(self, id):
        action_param = (
            db.session.query(DeviceActionParam)
            .filter(DeviceActionParam.id == id)
            .first()
        )
        db.session.delete(action_param)
        db.session.commit()
        return


@api_field.route("/", methods=["POST"])
class DeviceTypeFieldView(Resource):
    @api_field.expect(device_field_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def post(self):
        device_field = DeviceField()
        for param in device_field.columns():
            if param != "id":
                setattr(device_field, param, request.json[param])
        db.session.add(device_field)
        db.session.commit()
        return jsonify(
            {
                "id": device_field.id,
                "name": device_field.name,
                "unit": device_field.unit,
                "field_type": device_field.field_type,
                "device_type": device_field.device_type,
            }
        )


@api_field.route("/<int:id>", methods=["GET", "PATCH", "DELETE"])
class DeviceTypeFieldIdView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    def get(self, id):
        device_field = DeviceField.query.filter_by(id=id).first()
        if not device_field:
            abort(404)
        return jsonify(
            {
                "id": device_field.id,
                "name": device_field.name,
                "unit": device_field.unit,
                "field_type": device_field.field_type,
                "device_type": device_field.device_type,
            }
        )

    @api_field.expect(device_field_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def patch(self, id):
        device_field = DeviceField.query.filter_by(id=id).first()
        for param in device_field.columns():
            if param in request.json:
                setattr(device_field, param, request.json[param])
        db.session.add(device_field)
        db.session.commit()
        return jsonify(
            {
                "id": device_field.id,
                "name": device_field.name,
                "unit": device_field.unit,
                "field_type": device_field.field_type,
                "device_type": device_field.device_type,
            }
        )

    @api.doc(security="Bearer")
    @jwt_required()
    def delete(self, id):
        device_field = (
            db.session.query(DeviceField).filter(DeviceField.id == id).first()
        )
        db.session.delete(device_field)
        db.session.commit()
        return


class DeviceTypeUtils(Resource):
    def getActionParamsFields(self, id):
        params = DeviceActionParam.query.filter_by(action=id).all()
        action_params = []
        for param in params:
            action_param = {
                "id": param.id,
                "name": param.name,
                "param_type": param.param_type,
                "action": param.action,
            }
            action_params.append(action_param)
        return action_params

    def getActionsFields(self, id):
        actions = DeviceAction.query.filter_by(device_type=id).all()
        device_actions = []
        for action in actions:
            action_params = self.getActionParamsFields(action.id)
            device_action = {
                "id": action.id,
                "name": action.name,
                "function": action.function,
                "params": action_params,
            }
            device_actions.append(device_action)
        fields = DeviceField.query.filter_by(device_type=id).all()
        device_fields = []
        for field in fields:
            device_field = {
                "id": field.id,
                "name": field.name,
                "unit": field.unit,
                "field_type": field.field_type,
            }
            device_fields.append(device_field)
        return (device_actions, device_fields)
