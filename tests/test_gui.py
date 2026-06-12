import pytest
from gui import AutoClickerGUI


@pytest.fixture(scope="module")
def gui():
    g = AutoClickerGUI()
    yield g
    g._on_close()


def test_gui_initialization(gui):
    assert gui.root.title() == "连点器"
    assert gui.hotkey_var.get() == "F6"
    assert gui.mode_var.get() == "toggle"
    assert gui.interval_var.get() == 100


def test_gui_load_config(gui):
    config = gui.config_manager.load_config()
    assert "hotkey" in config
    assert "mode" in config


def test_gui_save_config(gui):
    gui.hotkey_var.set("F7")
    gui.save_config()
    config = gui.config_manager.load_config()
    assert config["hotkey"] == "F7"
    gui.hotkey_var.set("F6")
    gui.save_config()


def test_gui_toggle_clicking(gui):
    assert gui._running is False
    gui.toggle_clicking()
    assert gui._running is True
    assert "停止" in gui.start_button.cget("text")
    assert "运行中" in gui.status_label.cget("text")
    gui.toggle_clicking()
    assert gui._running is False
    assert "开始" in gui.start_button.cget("text")
    assert "停止" in gui.status_label.cget("text")
