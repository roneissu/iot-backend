from os import environ, urandom

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mqtt import Mqtt
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config["JSON_AS_ASCII"] = False
app.config["SWAGGER_UI_DOC_EXPANSION"] = "list"
app.secret_key = environ.get("SECRET_KEY") or urandom(24)
app.config["JWT_PUBLIC_KEY"] = environ.get("SECRET_KEY") or urandom(24)
app.config["JWT_SECRET_KEY"] = environ.get("SECRET_KEY") or urandom(24)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

app.config["MQTT_BROKER_URL"] = environ.get("BROKER_URL") or 'localhost'
app.config["MQTT_BROKER_PORT"] = int(environ.get("BROKER_PORT") or 1883)
app.config["MQTT_TLS_ENABLED"] = (environ.get("BROKER_TLS_ENABLED") == True) or False
app.config["MQTT_KEEPALIVE"] = 5

jwt = JWTManager(app)

mqtt_client = Mqtt(app)

api = Api(
    app,
    title="iot-backend",
    version="0.1",
    description="Projeto de TCC de Ronaldo Santos",
    authorizations=authorizations,
    security="apiKey"
)

from app.auth import api as auth_ns
from app.config import api as config_ns
from app.device import api as device_ns
from app.device import api_command as command_ns
from app.device_type import api as device_type_ns
from app.device_type import api_action as device_action_ns
from app.device_type import api_action_param as device_action_param_ns
from app.device_type import api_field as device_field_ns
from app.user import api as user_ns

api.add_namespace(auth_ns)
api.add_namespace(device_ns)
api.add_namespace(command_ns)
api.add_namespace(device_type_ns)
api.add_namespace(device_action_ns)
api.add_namespace(device_action_param_ns)
api.add_namespace(device_field_ns)
api.add_namespace(config_ns)
api.add_namespace(user_ns)


if __name__ == "__main__":
    app.run(debug=True)
