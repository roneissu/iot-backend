from os import environ
from dotenv import load_dotenv

load_dotenv()

user = environ.get("SERVER_USER")
password = environ.get("SERVER_PASS")
host = environ.get("SERVER_HOST")
port = environ.get("SERVER_PORT")
database = environ.get("SERVER_DB")
google_client_id = environ.get("GOOGLE_CLIENT_ID")
