# pyright: reportOptionalSubscript=false
from flask import abort, jsonify, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, fields

from app.database import User, db

api = Namespace('user', description='User CRUD')

user_model = api.model('UserModel', {
    'name': fields.String,
    'email': fields.String,
    'picture': fields.String
})

@api.route('/', methods=["GET", "POST"])
class UserView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
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
                'name': user.name,
                'email': user.email,
                'picture': user.picture,
                'devices': devices
            }
        return jsonify(res)

    @api.expect(user_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def post(self):
        user = User()
        for param in user.columns():
            if param != 'id':
                setattr(user, param, request.json[param])
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'picture': user.picture
        })


@api.route('/<int:id>', methods=["GET", "PATCH", "DELETE"])
class UserIdView(Resource):
    @api.doc(security="Bearer")
    @jwt_required()
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
            'name': user.name,
            'email': user.email,
            'picture': user.picture,
            'devices': devices
        }
        return jsonify(res)

    @api.expect(user_model)
    @api.doc(security="Bearer")
    @jwt_required()
    def patch(self, id):
        user = User.query.filter_by(id=id).first()
        for param in user.columns():
            if param in request.json:
                setattr(user, param, request.json[param])
        db.session.add(user)
        db.session.commit()
        devices = []
        for device in user.devices:
            devices.append({
                'id': device.id,
                'serie_number': device.serie_number,
                'alias_name': device.alias_name,
                'firmware_version': device.firmware_version
            })
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'picture': user.picture,
            'devices': devices
        })

    @api.doc(security="Bearer")
    @jwt_required()
    def delete(self, id):
        user = db.session.query(User).filter(User.id==id).first()
        db.session.delete(user)
        db.session.commit()
        return
    
    def user_by_email(self, email):
        try:
            return User.query.filter(User.email == email).first()
        except:
            return None