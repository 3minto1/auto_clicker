import pytest
from clicker import Clicker

def test_clicker_initialization():
    clicker = Clicker()
    assert clicker.target == "keyboard"
    assert clicker.key == "a"
    assert clicker.interval == 100
    assert clicker.is_clicking is False

def test_set_target_keyboard():
    clicker = Clicker()
    clicker.set_target("keyboard")
    assert clicker.target == "keyboard"

def test_set_target_mouse():
    clicker = Clicker()
    clicker.set_target("mouse")
    assert clicker.target == "mouse"

def test_set_target_invalid():
    clicker = Clicker()
    original = clicker.target
    clicker.set_target("invalid")
    assert clicker.target == original

def test_set_key():
    clicker = Clicker()
    clicker.set_key("b")
    assert clicker.key == "b"

def test_set_interval():
    clicker = Clicker()
    clicker.set_interval(50)
    assert clicker.interval == 50

def test_set_interval_minimum():
    clicker = Clicker()
    clicker.set_interval(1)
    assert clicker.interval == 1

def test_set_interval_maximum():
    clicker = Clicker()
    clicker.set_interval(1000)
    assert clicker.interval == 1000

def test_set_interval_below_minimum():
    clicker = Clicker()
    original = clicker.interval
    clicker.set_interval(0)
    assert clicker.interval == original

def test_set_interval_above_maximum():
    clicker = Clicker()
    original = clicker.interval
    clicker.set_interval(1001)
    assert clicker.interval == original

def test_set_interval_negative():
    clicker = Clicker()
    original = clicker.interval
    clicker.set_interval(-1)
    assert clicker.interval == original

def test_start_stop_clicking():
    clicker = Clicker()
    clicker.start_clicking()
    assert clicker.is_clicking is True
    clicker.stop_clicking()
    assert clicker.is_clicking is False

def test_double_start():
    clicker = Clicker()
    clicker.start_clicking()
    clicker.start_clicking()
    assert clicker.is_clicking is True
    clicker.stop_clicking()
