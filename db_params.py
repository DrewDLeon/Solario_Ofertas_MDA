from dotenv import load_dotenv
import os
load_dotenv()

class params:
    def __init__(self) :
        self.user = os.environ.get('DB_USER')
        self.password = os.environ.get('DB_PASSWORD')
        self.database = os.environ.get('DB_DATABASE')
        self.port = os.environ.get('DB_PORT')
        self.host = os.environ.get('DB_HOST')