import configparser
import Attacks.Mission1
import NoiseGenerator.Mission1.noise1
from mission import Mission
import Attacks.Mission1.exploit_jwt
import NoiseGenerator.Mission1.noise
from jsonlogger import setup_logger, log_with_custom_fields, JsonLogFormatter
import time
import random
import os
import importlib
class AttackFramework:
    
    missions: list[Mission]
    logger: JsonLogFormatter

    def __init__(self) -> None:
        # Init attack framework and load missions
        try:
            self.missions = list()
            config = configparser.ConfigParser()
            config.read("config.conf")
            self.logger = setup_logger("Logs/logs.json")

            for mission in config.sections():
                self.missions.append(Mission(config[mission]["name"], config[mission]["port"], int(mission[-1])))
        
        except Exception as e:
            print(e)
            exit(-1)

    def __check_response(self, response: str, target: str, message) -> bool:

        if "failed" in response:
            log_with_custom_fields(self.logger, message, target, "Flag stolen fail")
            return False
        
        log_with_custom_fields(self.logger, message, target, "Flag stolen succes")
        return True

    def start_attack(self):

        # Sleep between 1-360 seconds before every attack
        time.sleep(random.randint(1,360))

        for mission in self.missions:
            for target in mission.targets:
                try:
                    if mission.number == 1:
                        self.start_noise(mission.number)
                        Attacks.Mission1.exploit_jwt.exploit(target)
                        response = mission.submit_remote()
                        self.__check_response(response, target, f"Exploit 1 for mission f{mission.number}")
                    if mission.number == 2:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")
                    if mission.number == 3:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")  
                    if mission.number == 4:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")
                    if mission.number == 5:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")  
                    if mission.number == 6:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")
                    if mission.number == 7:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")  
                    if mission.number == 8:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")
                    if mission.number == 9:
                        print(f"[-]Exploit functions not implemented for mission f{mission.number}")  
                except Exception as e:
                    self.logger.debug(e)
                    exit(-1)        

    def start_noise(self, mission_number):
            
        try:
            if mission_number == 1:
                NoiseGenerator.Mission1.noise.noise()
                NoiseGenerator.Mission1.noise1.noise()
            if mission_number == 2:
                print(f"[-]Noise functions not implemented for mission f{mission_number}")
            if mission_number == 3:
                print(f"[-]Noise functions not implemented for mission f{mission_number}")  
            if mission_number == 4:
                print(f"[-]NOise functions not implemented for mission f{mission_number}")
            if mission_number == 5:
                print(f"[-]Noise functions not implemented for mission f{mission_number}")  
            if mission_number == 6:
                print(f"[-]Noise functions not implemented for mission f{mission_number}")
            if mission_number == 7:
                print(f"[-]Noise functions not implemented for mission f{mission_number}")  
            if mission_number == 8:
                print(f"[-]Noise functions not implemented for mission f{mission_number}")
            if mission_number == 9:
                print(f"[-]Noise functions not implemented for mission f{mission_number}")
        except Exception as e:
            self.logger.debug(e)
            exit(-1)






