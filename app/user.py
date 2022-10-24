from flask import abort, jsonify, request
from flask_restx import Namespace, Resource, fields
from app.database import db, User
from app.device import device_model


api = Namespace('user', description='User CRUD')

user_model = api.model('UserModel', {
    'username': fields.String,
    'password': fields.String,
    'name': fields.String,
    'email': fields.String,
    'date_nasc': fields.Date
})

@api.route('/', methods=["GET", "POST"])
class UserView(Resource):
    def get(self):
        users = User.query.paginate(1, 10).items
        res = []
        for user in users:
            devices = []
            for device in user.devices:
                devices.append({
                    'id': device.id,
                    'serie_number': device.serie_number,
                    'alias_name': device.alias_name,
                    'firmware_version': device.firmware_version
                })
            res = {
                'id': user.id,
                'username': user.username,
                'password': user.password,
                'name': user.name,
                'email': user.email,
                'date_nasc': user.date_nasc,
                'devices': devices
            }
        return jsonify(res)

    @api.expect(user_model)
    def post(self):
        user = User()
        for param in user.columns():
            if param != 'id':
                setattr(user, param, request.json[param])
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'name': user.name,
            'email': user.email,
            'date_nasc': user.date_nasc
        })


@api.route('/<int:id>', methods=["GET", "PATCH", "DELETE"])
class UserIdView(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        if not user:
            abort(404)
        devices = []
        for device in user.devices:
            devices.append({
                'id': device.id,
                'serie_number': device.serie_number,
                'alias_name': device.alias_name,
                'firmware_version': device.firmware_version
            })
        res = {
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'name': user.name,
            'email': user.email,
            'date_nasc': user.date_nasc,
            'devices': devices
        }
        return jsonify(res)

    @api.expect(user_model)
    def patch(self, id):
        user = User.query.filter_by(id=id).first()
        for param in user.columns():
            if param in request.json:
                setattr(user, param, request.json[param])
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'name': user.name,
            'email': user.email,
            'date_nasc': user.date_nasc
        })

    def delete(self, id):
        user = db.session.query(User).filter(User.id==id).first()
        db.session.delete(user)
        db.session.commit()
        return
    
    def user_by_username(username):
        try:
            return User.query.filter(User.username == username).one()
        except:
            return None