import pytest
from clicker import Clicker
from pynput import mouse


def test_mouse_button_left():
    clicker = Clicker()
    button = clicker.MOUSE_BUTTON_MAP.get("left")
    assert button == mouse.Button.left


def test_mouse_button_right():
    clicker = Clicker()
    button = clicker.MOUSE_BUTTON_MAP.get("right")
    assert button == mouse.Button.right


def test_mouse_button_middle():
    clicker = Clicker()
    button = clicker.MOUSE_BUTTON_MAP.get("middle")
    assert button == mouse.Button.middle


def test_mouse_button_default():
    clicker = Clicker()
    button = clicker.MOUSE_BUTTON_MAP.get("unknown", mouse.Button.left)
    assert button == mouse.Button.left


def test_clicker_mouse_simulation():
    clicker = Clicker()
    clicker.set_target("mouse")
    clicker.set_key("right")
    assert clicker.target == "mouse"
    assert clicker.key == "right"


def test_modifier_key_shift():
    clicker = Clicker()
    clicker.set_key("shift_l")
    from pynput import keyboard
    resolved = clicker._resolve_key("shift_l")
    assert resolved == keyboard.Key.shift_l


def test_modifier_key_ctrl():
    clicker = Clicker()
    clicker.set_key("ctrl")
    from pynput import keyboard
    resolved = clicker._resolve_key("ctrl")
    assert resolved == keyboard.Key.ctrl


def test_modifier_key_alt():
    clicker = Clicker()
    clicker.set_key("alt")
    from pynput import keyboard
    resolved = clicker._resolve_key("alt")
    assert resolved == keyboard.Key.alt


def test_normal_key_passes_through():
    clicker = Clicker()
    resolved = clicker._resolve_key("a")
    assert resolved == "a"
