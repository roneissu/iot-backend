from flask import abort, jsonify, request
from flask.json import dumps
from flask_restx import Namespace, Resource, fields
from app.database import Device, db, Config


api = Namespace("config", description="Config CRUD")

config_model = api.model(
    "ConfigModel",
    {
        "hour": fields.Integer,
        "minute": fields.Integer,
        "start_time": fields.DateTime,
        "end_time": fields.DateTime,
        "active": fields.Boolean,
        "slot": fields.Integer,
        "device_id": fields.Integer,
    },
)


@api.route("", methods=["GET", "POST"])
class ConfigView(Resource):
    def get(self):
        configs = Config.query.paginate(1, 10).items
        res = []
        for config in configs:
            res.append(
                {
                    "id": config.id,
                    "hour": config.hour,
                    "minute": config.minute,
                    "start_time": config.start_time,
                    "end_time": config.end_time,
                    "active": config.active,
                    "slot": config.slot,
                    "device_id": config.device_id,
                }
            )
        return jsonify(res)

    @api.expect(config_model)
    def post(self):
        config = Config()
        for param in config.columns():
            if param != "id":
                setattr(config, param, request.json[param])
        db.session.add(config)
        db.session.commit()

        self.add_config(config)

        return jsonify(
            {
                "id": config.id,
                "hour": config.hour,
                "minute": config.minute,
                "start_time": config.start_time,
                "end_time": config.end_time,
                "active": config.active,
                "slot": config.slot,
                "device_id": config.device_id,
            }
        )

    def add_config(self, config):
        pass
        # device = Device.query.filter_by(id=config.device_id).first()

        # publish(f'devices/{device.serie_number}/configs/add', dumps({'values': [{
        #     'slot': config.slot,
        #     'hour': config.hour,
        #     'minute': config.minute,
        #     'start_time': config.start_time,
        #     'end_time': config.end_time,
        #     'active': config.active
        # }]}))

    def delete_config(self, config):
        pass
        # device = Device.query.filter_by(id=config.device_id).first()

        # publish(f'devices/{device.serie_number}/configs/delete', dumps({'values': [{
        #     'slot': config.slot
        # }]}))


@api.route("/<int:id>", methods=["GET", "PATCH", "DELETE"])
class ConfigIdView(Resource):
    def get(self, id):
        config = Config.query.filter_by(id=id).first()
        if not config:
            abort(404)
        res = {
            "id": config.id,
            "hour": config.hour,
            "minute": config.minute,
            "start_time": config.start_time,
            "end_time": config.end_time,
            "active": config.active,
            "slot": config.slot,
            "device_id": config.device_id,
        }
        return jsonify(res)

    @api.expect(config_model)
    def patch(self, id):
        config = Config.query.filter_by(id=id).first()
        for param in config.columns():
            if param in request.json:
                setattr(config, param, request.json[param])
        db.session.add(config)
        db.session.commit()
        self.add_config(config)
        return jsonify(
            {
                "id": config.id,
                "hour": config.hour,
                "minute": config.minute,
                "start_time": config.start_time,
                "end_time": config.end_time,
                "active": config.active,
                "slot": config.slot,
                "device_id": config.device_id,
            }
        )

    def delete(self, id):
        config = db.session.query(Config).filter(Config.id == id).first()
        db.session.delete(config)
        db.session.commit()

        self.delete_config(config)

        return "OK"

    def add_config(self, config):
        pass
        # device = Device.query.filter_by(id=config.device_id).first()

        # publish(f'devices/{device.serie_number}/configs/add', dumps({'values': [{
        #     'slot': config.slot,
        #     'hour': config.hour,
        #     'minute': config.minute,
        #     'start_time': config.start_time,
        #     'end_time': config.end_time,
        #     'active': config.active
        # }]}))

    def delete_config(self, config):
        pass
        # device = Device.query.filter_by(id=config.device_id).first()

        # publish(f'devices/{device.serie_number}/configs/delete', dumps({'values': [{
        #     'slot': config.slot
        # }]}))
