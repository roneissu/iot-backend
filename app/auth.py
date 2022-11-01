# pyright: reportOptionalSubscript=false
import datetime
import time
from app import app, db_configs
from flask import jsonify, request, abort
from flask_restx import Namespace, Resource, fields
from app.database import db, User
from flask_jwt_extended import create_access_token, decode_token, jwt_required
from jwt import decode


api = Namespace("auth", description="Auth CRUD")
auth_model = api.model("AuthModel", {"token": fields.String})
secret_key = app.config.get("SECRET_KEY")


@api.route("/", methods=["POST"])
class AuthView(Resource):
    @api.expect(auth_model)
    def post(self):
        try:
            if request.json and secret_key:
                token = request.json.get("token", None)
                infos = decode(token, options={"verify_signature": False})
                if infos.get("exp", 0) > time.time():
                    if infos.get("aud") == db_configs.google_client_id:
                        user = User.query.filter(User.email == infos.get("email")).first()
                        if not user:
                            try:
                                user = User()
                                user.name = infos.get("name")
                                user.email = infos.get("email")
                                user.picture = infos.get("picture")
                                db.session.add(user)
                                db.session.commit()
                            except:
                                abort(500)

                        access_token = create_access_token(identity=user.email)
                        res = {
                            "id": user.id,
                            "email": user.email,
                            "picture": user.picture,
                            "name": user.name,
                            "token": f'Bearer {access_token}'
                        }

                        return jsonify(res)
            return abort(404, "Error")
        except Exception as e:
            return abort(500, "Error")


@api.route("/logout", methods=["POST"])
class LogoutView(Resource):
    @api.expect(auth_model)
    def post(self):
        return jsonify({})
