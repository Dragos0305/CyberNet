import Attacks.Mission1
import Attacks.Mission1.exploit_jwt
from utils import Utils
import requests
from fake_useragent import UserAgent
import Attacks.Mission1

def submit_flags(flag_list: list) -> None:
    pass

class Target:
    
    host: str
    port: int
    

    def __init__(self, host: str, port: int = 80) -> None:
        self.host = host
        self.port = port
  
        print(f"Target {host}:{port} added")


    def __create_noise() -> None:
        # Use utils functions to initiate session for web based applications
        print("[+]Fake attacks generator to obscure real attacks")
   
    

