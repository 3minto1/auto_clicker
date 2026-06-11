import os
import json
import pytest
from config_manager import ConfigManager

def test_load_default_config(tmp_path):
    config_file = str(tmp_path / "test_config.json")
    config_manager = ConfigManager(config_file)
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

def test_reset_config():
    config_manager = ConfigManager()
    config_manager.save_config({"hotkey": "F9", "mode": "hold", "interval": 200})
    reset_config = config_manager.reset_config()
    assert reset_config == config_manager.default_config
    loaded = config_manager.load_config()
    assert loaded == config_manager.default_config
    os.remove(config_manager.config_file)

def test_load_nonexistent_config():
    config_manager = ConfigManager("nonexistent.json")
    config = config_manager.load_config()
    assert config == config_manager.default_config

def test_config_values_types():
    config_manager = ConfigManager()
    config = config_manager.load_config()
    assert isinstance(config["hotkey"], str)
    assert isinstance(config["mode"], str)
    assert isinstance(config["interval"], int)
    assert isinstance(config["target"], str)
    assert isinstance(config["key"], str)

def test_save_and_load_multiple_times():
    config_manager = ConfigManager()
    for i in range(3):
        config = {"hotkey": f"F{i+6}", "mode": "toggle", "interval": 100 * (i+1)}
        config_manager.save_config(config)
        loaded = config_manager.load_config()
        assert loaded == config
    os.remove(config_manager.config_file)