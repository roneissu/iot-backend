# pyright: reportOptionalSubscript=false
import json
from flask import abort, jsonify, request
from flask_restx import Namespace, Resource, fields
from app import mqtt_client
from app.database import DeviceAction, DeviceActionParam, db, Device, users_devices, User
from flask_jwt_extended import jwt_required


api = Namespace("device", description="Device CRUD")
api_command = Namespace("device/command", description="Device CRUD command")

device_model = api.model(
    "DeviceModel",
    {
        "serie_number": fields.String,
        "alias_name": fields.String,
        "firmware_version": fields.String,
        "device_type": fields.Integer,
        "user_id": fields.Integer
    },
)

command_param_model = api.model(
    "CommandParamModel", {
        "param_id": fields.Integer,
        "value": fields.String,
    }
)

command_model = api.model(
    "CommandModel", {
        "command_id": fields.Integer,
        "params": fields.List(fields.Nested(command_param_model))
    }
)


@api.route("/", methods=["GET", "POST"])
class DeviceView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    def get(self):
        devices = Device.query.all()
        res = []
        for device in devices:
            res.append(
                {
                    "id": device.id,
                    "serie_number": device.serie_number,
                    "alias_name": device.alias_name,
                    "firmware_version": device.firmware_version,
                    "device_type": device.device_type,
                }
            )
        return jsonify(res)

    @api.expect(device_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def post(self):
        user = User.query.filter(User.id == request.json["user_id"]).first()
        device = Device()
        for param in device.columns():
            if param != "id" and param != "user_id":
                setattr(device, param, request.json[param])
        db.session.add(device)
        db.session.commit()
        db.session.execute(
            users_devices.insert(), params={"user_id": user.id, "device_id": device.id}
        )
        db.session.commit()
        return jsonify(
            {
                "id": device.id,
                "serie_number": device.serie_number,
                "alias_name": device.alias_name,
                "firmware_version": device.firmware_version,
                "device_type": device.device_type,
            }
        )


@api.route("/<int:id>", methods=["GET", "PATCH", "DELETE"])
class DeviceIdView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    def get(self, id):
        device = Device.query.filter_by(id=id).first()
        if not device:
            abort(404)
        res = {
            "id": device.id,
            "serie_number": device.serie_number,
            "alias_name": device.alias_name,
            "firmware_version": device.firmware_version,
            "device_type": device.device_type,
        }
        return jsonify(res)

    @api.expect(device_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def patch(self, id):
        device = Device.query.filter_by(id=id).first()
        for param in device.columns():
            if param in request.json:
                setattr(device, param, request.json[param])
        db.session.add(device)
        db.session.commit()
        return jsonify(
            {
                "id": device.id,
                "serie_number": device.serie_number,
                "alias_name": device.alias_name,
                "firmware_version": device.firmware_version,
                "device_type": device.device_type,
            }
        )

    @api.doc(security="Bearer")
    @jwt_required()
    def delete(self, id):
        device = db.session.query(Device).filter(Device.id == id).first()
        db.session.delete(device)
        db.session.commit()
        return


class DeviceUtils():
    @staticmethod
    def sortParams(value):
        return value["order"]
    
    @staticmethod
    def getParamType(param_int):
        match param_int:
            case 0:
                return "string"
            case 1:
                return "integer"
            case 2:
                return "float"
            case 3:
                return "boolean"
            case 4:
                return "date"
            case 5:
                return "time"


@api_command.route("/<int:id>", methods=["POST"])
class DeviceCommandView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
    @api.expect(command_model)
    def post(self, id):
        device = Device.query.filter_by(id=id).first()
        device_action = DeviceAction.query.filter_by(id=request.json["command_id"]).first()

        params = {}
        for idx, param in enumerate(request.json["params"]):
            action_param = DeviceActionParam.query.filter_by(id=param["param_id"]).first()
            params[idx] = {
                "name": action_param.name,
                "type": DeviceUtils.getParamType(action_param.param_type),
                "value": param["value"]
            }

        topic = f'medicare/{device.serie_number}/command'
        command = {
            "command": device_action.name,
            "params": params
        }
        publish_result = mqtt_client.publish(topic, json.dumps(command, indent=4).encode('utf-8'))
        return jsonify(
            {
                "result": True,
                "topic": topic,
                "command": command,
                "result": publish_result,
                "message": f'Command sended to {device.alias_name}',
            }
        )
