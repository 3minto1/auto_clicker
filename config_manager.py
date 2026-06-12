import json
import os


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "hotkey": "F6",
            "mode": "toggle",
            "interval": 100,
            "target": "keyboard",
            "key": "a",
            "close_to_tray": True
        }

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                for k, v in self.default_config.items():
                    config.setdefault(k, v)
                return config
        return self.default_config.copy()

    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def reset_config(self):
        self.save_config(self.default_config.copy())
        return self.default_config.copy()
