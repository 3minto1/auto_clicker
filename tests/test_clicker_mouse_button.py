import pytest
from clicker import Clicker
from pynput import mouse

def test_get_mouse_button_left():
    clicker = Clicker()
    button = clicker._get_mouse_button("left")
    assert button == mouse.Button.left

def test_get_mouse_button_right():
    clicker = Clicker()
    button = clicker._get_mouse_button("right")
    assert button == mouse.Button.right

def test_get_mouse_button_middle():
    clicker = Clicker()
    button = clicker._get_mouse_button("middle")
    assert button == mouse.Button.middle

def test_get_mouse_button_default():
    clicker = Clicker()
    button = clicker._get_mouse_button("unknown")
    assert button == mouse.Button.left

def test_clicker_mouse_simulation():
    clicker = Clicker()
    clicker.set_target("mouse")
    clicker.set_key("right")
    assert clicker.target == "mouse"
    assert clicker.key == "right"