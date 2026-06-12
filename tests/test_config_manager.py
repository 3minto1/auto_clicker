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


def test_save_config(tmp_path):
    config_file = str(tmp_path / "test_config.json")
    config_manager = ConfigManager(config_file)
    test_config = {"hotkey": "F6", "mode": "toggle", "interval": 50}
    config_manager.save_config(test_config)
    loaded_config = config_manager.load_config()
    for k, v in test_config.items():
        assert loaded_config[k] == v


def test_reset_config(tmp_path):
    config_file = str(tmp_path / "test_config.json")
    config_manager = ConfigManager(config_file)
    config_manager.save_config({"hotkey": "F9", "mode": "hold", "interval": 200})
    reset_config = config_manager.reset_config()
    assert reset_config == config_manager.default_config
    loaded = config_manager.load_config()
    assert loaded == config_manager.default_config


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
    assert isinstance(config["close_to_tray"], bool)


def test_save_and_load_multiple_times(tmp_path):
    config_file = str(tmp_path / "test_config.json")
    config_manager = ConfigManager(config_file)
    for i in range(3):
        config = {"hotkey": f"F{i+6}", "mode": "toggle", "interval": 100 * (i+1)}
        config_manager.save_config(config)
        loaded = config_manager.load_config()
        for k, v in config.items():
            assert loaded[k] == v
