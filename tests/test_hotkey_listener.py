import pytest
from hotkey_listener import HotkeyListener

def test_hotkey_listener_initialization():
    listener = HotkeyListener()
    assert listener.current_hotkey == "F6"
    assert listener.mode == "toggle"

def test_set_hotkey():
    listener = HotkeyListener()
    listener.set_hotkey("F7")
    assert listener.current_hotkey == "F7"

def test_set_mode():
    listener = HotkeyListener()
    listener.set_mode("hold")
    assert listener.mode == "hold"
