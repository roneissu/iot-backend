from json import dumps
import json
from os import environ, urandom

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mqtt import Mqtt
from flask_restx import Api
from flask_socketio import SocketIO, emit
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JSON_AS_ASCII"] = False
app.config["SWAGGER_UI_DOC_EXPANSION"] = "list"
app.secret_key = environ.get("SECRET_KEY") or urandom(24)
app.config["JWT_PUBLIC_KEY"] = environ.get("SECRET_KEY") or urandom(24)
app.config["JWT_SECRET_KEY"] = environ.get("SECRET_KEY") or urandom(24)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

app.config["MQTT_BROKER_URL"] = environ.get("BROKER_URL") or "localhost"
app.config["MQTT_BROKER_PORT"] = int(environ.get("BROKER_PORT") or 1883)
app.config["MQTT_TLS_ENABLED"] = (environ.get("BROKER_TLS_ENABLED") == True) or False
app.config["MQTT_KEEPALIVE"] = 5

jwt = JWTManager(app)

mqtt_client = Mqtt(app)

socketio = SocketIO(app, cors_allowed_origins="*")

api = Api(
    app,
    title="iot-backend",
    version="0.1",
    description="Projeto de TCC de Ronaldo Santos",
    authorizations=authorizations,
    security="apiKey",
)

BASE_TOPIC = "medicare/"
COMMAND_TOPIC = BASE_TOPIC + "command/"
COMMAND_RES_TOPIC = BASE_TOPIC + "commandresult/"
VALUES_TOPIC = BASE_TOPIC + "values/"

commands_awaiting = dict()

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


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected!")
        mqtt_client.subscribe(BASE_TOPIC + "#")
        print("subscribed")
    else:
        print('Error in connection', rc)


@mqtt_client.on_topic(COMMAND_RES_TOPIC + "+")
def handle_mqtt_command_res(client, userdata, message):
    serie_number = str(message.topic).split(COMMAND_RES_TOPIC)[1]
    message_val = json.loads(message.payload.decode())
    if message_val['hash'] in commands_awaiting:
        command_res = commands_awaiting[message_val['hash']]
        socketio.emit("command", { 'command': command_res, 'serie_number': serie_number, 'result': message_val['result'] })
        del commands_awaiting[message_val['hash']]


@mqtt_client.on_topic(VALUES_TOPIC + "+")
def handle_mqtt_values(client, userdata, message):
    serie_number = str(message.topic).split(VALUES_TOPIC)[1]
    if not message.payload.decode().__eq__('Connected'):
        for key, field in (dict)(json.loads(message.payload.decode())).items():
            message = { 'msg': { 'serie_number': serie_number, 'name': key, 'value': field } }
            socketio.emit("values", message)
            print('Sended: ', json.dumps(message))


mqtt_client._connect()


@socketio.on("message")
def handle_message(data):
    print("received message: " + dumps(data))
    socketio.emit("message", {"test": 123})


if __name__ == "__main__":
    socketio.run(app, debug=True)
