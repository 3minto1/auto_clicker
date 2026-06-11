import pytest
from clicker import Clicker

def test_clicker_initialization():
    clicker = Clicker()
    assert clicker.target == "keyboard"
    assert clicker.key == "a"
    assert clicker.interval == 100

def test_set_target():
    clicker = Clicker()
    clicker.set_target("mouse")
    assert clicker.target == "mouse"

def test_set_key():
    clicker = Clicker()
    clicker.set_key("b")
    assert clicker.key == "b"

def test_set_interval():
    clicker = Clicker()
    clicker.set_interval(50)
    assert clicker.interval == 50
