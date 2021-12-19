from dotenv import load_dotenv
from os import getenv


class Keys:
    def __init__(self):
        ...

    def __dict__(self):
        ...


    def refresh_env(self):
        load_dotenv()
        self.load_keys()

    def load_keys(self):
        ...


