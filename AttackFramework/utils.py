from PIL import Image
import pytesseract
import numpy as np
import requests
from fake_useragent import UserAgent

class Utils:

    @staticmethod
    def get_text_from_image(image_content: bytes) -> str:
        pass

    @staticmethod
    def download_resource() -> bytes:
        
        try:
            resource_url = "" # resource url here
            content = requests.get(resource_url).content
            return content
        except Exception as e:
            print(e)
            return None
        
    @staticmethod
    def init_headers() -> dict:

        # Default headers for the attack
        ua = UserAgent()
        headers = {
        "User-Agent": ua.random,
        'Accept-Language': 'en-US,en;q=0.5',  
        'Accept-Encoding': 'gzip, deflate',    
        }

        return headers        
     

    @staticmethod
    def init_session() -> requests.Session:
        try:
            session = requests.Session()
            headers = Utils.init_headers()
            session.headers.update(headers)
            session.headers
            session.verify = False
            return session
        
        except Exception as e:
            print(e)
            print("[-]Something went wrong in init_session function")
            exit(-1)
            

