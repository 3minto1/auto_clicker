import pytest
from gui import AutoClickerGUI

def test_gui_initialization():
    gui = AutoClickerGUI()
    assert gui.root.title() == "连点器"
    assert gui.hotkey_var.get() == "F6"
    assert gui.mode_var.get() == "toggle"
    assert gui.interval_var.get() == 100
