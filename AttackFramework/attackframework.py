import configparser
import Attacks.Mission1
from mission import Mission
import Attacks.Mission1.exploit_jwt
from jsonlogger import setup_logger, log_with_custom_fields, JsonLogFormatter

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

    def __check_response(response: str) -> bool:
        if "failed" in response:
            return False
        return True

    def start_attack(self):
        for mission in self.missions:
            for target in mission.targets:
                if mission.number == 1:
                    Attacks.Mission1.exploit_jwt.exploit(target)
                    response = mission.submit_remote()

                    if response == True:
                        log_with_custom_fields(self.logger,"Custom message", target, "Attack exploit 1", "Flag stolen")
                    else:
                        log_with_custom_fields(self.logger,"Custom message", target, "Attack exploit 1", "Flag stolen fail")
                    


                if mission.number == 2:
                    print("[-]Exploit functions not implemented")  

    def start_noise(self):
        pass







