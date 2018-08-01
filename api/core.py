from dispatcher import dispatcher
from datetime import datetime

from HardwareRepository import HardwareRepository


hw_repository_client = HardwareRepository.HardwareRepository()
#TODO do some clever maping here via csv file
sample_changer_hwobj = hw_repository_client.getHardwareObject("sc-mockup")


class CoreComponent():
    def __init__(self, name=""):
        self.name = name

    def connect_signal(self, signal_name, callable_func):
        try:
            dispatcher.disconnect(callable_func, signal_name, self.name)
        except:
            pass
        dispatcher.connect(callable_func, signal_name, self.name)

  
    def send_signal(self, signal_name, data):
        data["sender"] = self.name
        data["timestamp"] = datetime.now()   

        dispatcher.send(signal_name, self.name, data)        
