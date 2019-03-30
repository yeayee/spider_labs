import time
from multiprocessing import Process
from api import app
from getter import Getter
from tester import Tester
from db import RedisClient
from setting import *

class Scheduler:
    def schedule_tester(self, cycle=TESTER_CYCLE):
        tester = Tester()
        while True:
            print("start test proxy")
            tester.run()
            time.sleep(cycle)
    
    def schedule_getter(self, cycle=GETTER_CYCLE):
        getter = Getter()
        while True:
            print("start get proxy")
            getter.run()
            time.sleep(cycle)
    
    def schedule_api(self):
        app.run()
    
    def run(self):
        print("Proxy Pool is running")

        if TESTER_ENABLED:
            test_process = Process(target=self.schedule_tester)
            test_process.start()

        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()

        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()

        