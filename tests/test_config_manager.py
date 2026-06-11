import os
import json
import pytest
from config_manager import ConfigManager

def test_load_default_config():
    config_manager = ConfigManager()
    config = config_manager.load_config()
    assert "hotkey" in config
    assert "mode" in config
    assert "interval" in config
    assert config["interval"] == 100

def test_save_config():
    config_manager = ConfigManager()
    test_config = {"hotkey": "F6", "mode": "toggle", "interval": 50}
    config_manager.save_config(test_config)
    loaded_config = config_manager.load_config()
    assert loaded_config == test_config
    os.remove(config_manager.config_file)