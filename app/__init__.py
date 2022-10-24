from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['JSON_AS_ASCII'] = False
app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'

api = Api(
    app,
    title='iot-backend',
    version='0.1',
    description='Projeto de TCC de Ronaldo Santos'
)

from app.device import api as device_ns, api_command as command_ns
from app.device_type import api as device_type_ns, api_action as device_action_ns, api_field as device_field_ns
from app.config import api as config_ns
from app.user import api as user_ns
api.add_namespace(device_ns)
api.add_namespace(command_ns)
api.add_namespace(device_type_ns)
api.add_namespace(device_action_ns)
api.add_namespace(device_field_ns)
api.add_namespace(config_ns)
api.add_namespace(user_ns)

@app.route("/")
def hello_world():
    return "<h1>Hi</h1><p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(debug=True)
