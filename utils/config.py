import json
from os import path

# config.py
class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.cfg = None

    def load_cfg(self, config_file):
        if not path.exists("config.json"):
            raise FileNotFoundError(
                "config.json not found. Please: copy, config, and rename `config.json.example` to `config.json`"
            )
        with open(config_file, 'r') as f:
            self.cfg = json.load(f)