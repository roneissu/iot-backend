from flask import abort, jsonify, request
from flask_restx import Namespace, Resource, fields
from app.database import db, Device, DeviceType, users_devices, User


api = Namespace('device', description='Device CRUD')
api_command = Namespace('device/command', description='Device CRUD command')

device_model = api.model('DeviceModel', {
    'serie_number': fields.String,
    'alias_name': fields.String,
    'firmware_version': fields.String,
    'device_type': fields.Integer
})

@api.route('/', methods=["GET", "POST"])
class DeviceView(Resource):
    def get(self):
        devices = Device.query.all()
        res = []
        for device in devices:
            device_type = DeviceType()
            if (device.device_type is not None) and device.device_type > 0:
                device_type = DeviceType.query.filter_by(id=device.device_type).first()
            res.append({
                'id': device.id,
                'serie_number': device.serie_number,
                'alias_name': device.alias_name,
                'firmware_version': device.firmware_version,
                'device_type': device.device_type
            })
        return jsonify(res)

    @api.expect(device_model)
    def post(self):
        user = User.query.first()
        device = Device()
        for param in device.columns():
            if param != 'id':
                setattr(device, param, request.json[param])
        db.session.add(device)
        db.session.commit()
        db.session.execute(
            users_devices.insert(),
            params={'user_id': user.id, 'device_id': device.id}
        )
        db.session.commit()
        device_type = DeviceType()
        if (device.device_type is not None) and device.device_type > 0:
            device_type = DeviceType.query.filter_by(id=device.device_type).first()
        return jsonify({
            'id': device.id,
            'serie_number': device.serie_number,
            'alias_name': device.alias_name,
            'firmware_version': device.firmware_version,
            'device_type': device.device_type
        })


@api.route('/<int:id>', methods=["GET", "PATCH", "DELETE"])
class DeviceIdView(Resource):
    def get(self, id):
        device = Device.query.filter_by(id=id).first()
        if not device:
            abort(404)
        device_type = DeviceType()
        if (device.device_type is not None) and device.device_type > 0:
            device_type = DeviceType.query.filter_by(id=device.device_type).first()
        res = {
            'id': device.id,
            'serie_number': device.serie_number,
            'alias_name': device.alias_name,
            'firmware_version': device.firmware_version,
            'device_type': device.device_type
        }
        return jsonify(res)

    @api.expect(device_model)
    def patch(self, id):
        device = Device.query.filter_by(id=id).first()
        for param in device.columns():
            if param in request.json:
                setattr(device, param, request.json[param])
        db.session.add(device)
        db.session.commit()
        device_type = DeviceType()
        if (device.device_type is not None) and device.device_type > 0:
            device_type = DeviceType.query.filter_by(id=device.device_type).first()
        return jsonify({
            'id': device.id,
            'serie_number': device.serie_number,
            'alias_name': device.alias_name,
            'firmware_version': device.firmware_version,
            'device_type': device.device_type
        })

    def delete(self, id):
        device = db.session.query(Device).filter(Device.id==id).first()
        db.session.delete(device)
        db.session.commit()
        return


@api_command.route('/<int:id>', methods=["POST"])
class DeviceCommandView(Resource):
    def post(self, id):
        device = Device.query.filter_by(id=id).first()
        return f'Command sended to {device.alias_name}'