import pytest
from hotkey_listener import HotkeyListener

def test_hotkey_listener_initialization():
    listener = HotkeyListener()
    assert listener.current_hotkey == "F6"
    assert listener.mode == "toggle"
    assert listener.is_listening is False

def test_set_hotkey():
    listener = HotkeyListener()
    listener.set_hotkey("F7")
    assert listener.current_hotkey == "F7"

def test_set_hotkey_modifier():
    listener = HotkeyListener()
    listener.set_hotkey("Ctrl+Shift+A")
    assert listener.current_hotkey == "Ctrl+Shift+A"

def test_set_mode_toggle():
    listener = HotkeyListener()
    listener.set_mode("toggle")
    assert listener.mode == "toggle"

def test_set_mode_hold():
    listener = HotkeyListener()
    listener.set_mode("hold")
    assert listener.mode == "hold"

def test_set_mode_invalid():
    listener = HotkeyListener()
    original = listener.mode
    listener.set_mode("invalid")
    assert listener.mode == original

def test_start_stop_listening():
    listener = HotkeyListener()
    callback = lambda: None
    listener.start_listening(callback)
    assert listener.is_listening is True
    assert listener.callback == callback
    listener.stop_listening()
    assert listener.is_listening is False
