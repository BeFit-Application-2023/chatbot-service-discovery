# Importing all needed libraries.
from flask import Flask, request
import threading

# Importing all needed modules.
from config import ConfigManager
from cerber import SecurityManager
from schemas import ServiceInfoSchema, GetMultipleServicesSchema
from service_manager import ServiceManager

# Loading the configurations.
config = ConfigManager("config.ini")

# Creation of the security Manager.
security_manager = SecurityManager(config.security.secret_key)

# Creation of the Validation Schemas.
service_info_schema = ServiceInfoSchema()
get_multiple_services_schema = GetMultipleServicesSchema()

# Creation of the Service Manager.
servicemanager = ServiceManager()

# Creation of the Flask application.
app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    # Checking the access token.
    check_response = security_manager.check_request(request)
    if check_response != "OK":
        return check_response, check_response["code"]
    else:
        status_code = 200

        # Validating the request.
        result, status_code = service_info_schema.validate_json(request.json)
        if status_code != 200:
            return result, status_code
        else:
            # Adding the service to the Service Registry.
            result, status_code = servicemanager.create(request.json)

            return result, status_code

@app.route("/get_all", methods=["GET"])
def get_all():
    # Checking the access token.
    check_response = security_manager.check_request(request)
    if check_response != "OK":
        return check_response, check_response["code"]
    else:
        # Getting the all services credentials.
        result, status_code = servicemanager.read_all()

        return result, status_code

@app.route("/get_services", methods=["GET"])
def get_services():
    # Checking the access token.
    check_response = security_manager.check_request(request)
    if check_response != "OK":
        return check_response, check_response["code"]
    else:
        status_code = 200

        # Validating the request.
        result, status_code = get_multiple_services_schema.validate_json(request.json)
        if status_code != 200:
            return result, status_code
        else:
            # Getting the credentials of the provided list of services.
            result, status_code = servicemanager.read_some(
                request.json["service_names"]
            )
            return result, status_code

@app.route("/update/<name>", methods=["PUT"])
def update(name):
    # Checking the access token.
    check_response = security_manager.check_request(request)
    if check_response != "OK":
        return check_response, check_response["code"]
    else:
        status_code = 200

        # Validating the request.
        result, status_code = service_info_schema.validate_json(request.json)
        if status_code != 200:
            return result, status_code
        else:
            # Updating the information of the service.
            result, status_code = servicemanager.update(name, request.json)
            return result, status_code

@app.route("/delete/<name>", methods=["DELETE"])
def delete(name):
    # Checking the access token.
    check_response = security_manager.check_request(request)
    if check_response != "OK":
        return check_response, check_response["code"]
    else:
        # Deleting the service from the Service Registry.
        result, status_code = servicemanager.delete(name)
        return result, status_code


@app.route("/heartbeat/<name>", methods=["POST"])
def heartbeat(name):
    # Checking the access token.
    check_response = security_manager.check_request(request)
    if check_response != "OK":
        return check_response, check_response["code"]
    else:
        # Extracting the status code and adding the heartbeat of the service.
        status_code = request.json["status_code"]
        result, status_code = servicemanager.add_heartbeat(name, status_code)
        return result, status_code

# Running the checking of the heartbeats.
threading.Thread(target=servicemanager.check_heartbeats).start()
app.run(
    host = config.general.host,
    port = config.general.port
)