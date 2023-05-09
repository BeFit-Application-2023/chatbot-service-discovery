# Importing all needed libraries.
import time
import threading


class ServiceManager:
    def __init__(self):
        '''
            The constructor of the Service Manager.
        '''
        self.service_dictionary = {}
        self.service_heartbeat = {}
        self.service_heartbeat_lock = threading.Lock()
        self.heartbeat_threshold = 70

    def create(self, service_info : dict) -> dict:
        '''
            This function adds the service information to the Service Registry.
                :param service_info: dict
                    The information about the service.
                :return: dict
                    The information of the service.
        '''
        # Adding the service do the Service Dictionary.
        self.service_dictionary[
            service_info["general"]["name"]
        ] = service_info

        # Adding the last checkpoint of the Service.
        self.service_heartbeat[
            service_info["general"]["name"]
        ] = time.time()
        return service_info, 200

    def read_all(self) -> dict:
        '''
            This function returns information about all registered services.
                :return: dict
                    The information of all services.
        '''
        return self.service_dictionary, 200

    def read_some(self, names : list) -> dict:
        '''
            This function returns the information of the services which names are in the argument names.
                :param names: list
                    The list with the names of the services.
                :return: dict
                    The information of the selected services or error message..
        '''
        # Checking if all services are in service registry.
        all_services_exists = all([name in self.service_dictionary for name in names])
        if all_services_exists:
            # Creating the services dictionary and returning it.
            requested_services = {
                name : self.service_dictionary[name]
                for name in names
            }
            return requested_services, 200
        else:
            # Checking the missing names and returning them with a status code 404.
            missing_names = []
            for name in names:
                if name not in self.service_dictionary:
                    missing_names.append(name)
            return {
                "missing_names" : missing_names
            }, 404

    def update(self, name : str, service_info : dict) -> dict:
        '''
            This function updates the information about a service.
                :param name: str
                    The name of the service to update.
                :param service_info: dict
                    The new information about a service.
                :return: dict
                    The new information of the service stored or error message..
        '''
        # Checking if such a service exists in the registry.
        if name in self.service_dictionary:
            # Updating the service information and returning it.
            self.service_dictionary[name].update(service_info)
            return self.service_dictionary[name], 200
        else:
            # Returning the error message if the service is not registered.
            return {
                "message" : "No such service",
            }, 404

    def delete(self, name : str) -> dict:
        '''
            This function deletes a service from the service registry.
                :param name: str
                    The name of the service to be deleted.
                :return: dict
                    The information of the deleted service or error message.
        '''
        if name in self.service_dictionary:
            service_info = self.service_dictionary.pop(name)
            self.service_heartbeat.pop(name)
            return service_info, 200
        else:
            return {
                "message" : "No such service",
            }, 404

    def add_heartbeat(self, name : str, status_code : int) -> dict:
        '''
            This function updates the last unix time point of a service.
                :param name: str
                    The name of the service that sent the heartbeat request.
                :param status_code: int
                    The status code of the request.
                :return: dict
                    The response sent to the service.
        '''
        # Acquiring the heartbeat lock.
        self.service_heartbeat_lock.acquire()

        # Checking if the service is registered.
        if name in self.service_heartbeat:

            # Updating the last heartbeat time point of service.
            self.service_heartbeat[name] = time.time()
            print(f"Service: {name}\nStatus code: {status_code}")

            # Releasing the heartbeat lock and returning confirmation message..
            self.service_heartbeat_lock.release()
            return {
                "message" : "Heartbeat confirmed!"
            }, 200
        else:
            # Releasing the heartbeat lock and returning the error message.
            self.service_heartbeat_lock.release()
            return {
                "message" : "No such service!"
            }, 404

    def check_heartbeats(self):
        '''
            This function checks in parallel the last time points of heartbeats sent by services
            and find the services that sent the heartbeat more than 70 s ago and report them to the
            Monitoring Service.
        '''
        while True:
            # Acquiring the heartbeat lock.
            self.service_heartbeat_lock.acquire()
            for service_name in self.service_heartbeat:
                # Checking if the service sent the heartbeat more than 70 s ago.
                if time.time() - self.service_heartbeat[service_name] > self.heartbeat_threshold:
                    # TODO: Sent request to the Service Monitoring.
                    print(service_name)
            self.service_heartbeat_lock.release()
            time.sleep(30)