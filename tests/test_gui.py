import os
import pytest
from gui import AutoClickerGUI

@pytest.fixture(scope="module")
def gui():
    g = AutoClickerGUI()
    yield g
    g.root.destroy()

def test_gui_initialization(gui):
    assert gui.hotkey_var.get() == "F6"
    assert gui.mode_var.get() == "toggle"
    assert gui.interval_var.get() == 100
    assert gui.target_var.get() == "keyboard"
    assert gui.key_var.get() == "a"

def test_gui_load_config(gui):
    gui.config_manager.save_config({
        "hotkey": "F7", "mode": "hold", "interval": 200,
        "target": "mouse", "key": "b"
    })
    gui.load_config()
    assert gui.hotkey_var.get() == "F7"
    assert gui.mode_var.get() == "hold"
    assert gui.interval_var.get() == 200
    assert gui.target_var.get() == "mouse"
    assert gui.key_var.get() == "b"
    os.remove(gui.config_manager.config_file)

def test_gui_save_config(gui):
    gui.hotkey_var.set("F8")
    gui.mode_var.set("hold")
    gui.interval_var.set(300)
    gui.target_var.set("mouse")
    gui.key_var.set("c")
    gui.save_config()
    loaded = gui.config_manager.load_config()
    assert loaded["hotkey"] == "F8"
    assert loaded["mode"] == "hold"
    assert loaded["interval"] == 300
    assert loaded["target"] == "mouse"
    assert loaded["key"] == "c"
    os.remove(gui.config_manager.config_file)

def test_gui_toggle_clicking(gui):
    assert gui.clicker.is_clicking is False
    gui.toggle_clicking()
    assert gui.clicker.is_clicking is True
    assert gui.start_button.cget("text") == "停止"
    gui.toggle_clicking()
    assert gui.clicker.is_clicking is False
    assert gui.start_button.cget("text") == "开始"
