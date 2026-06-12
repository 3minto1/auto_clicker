import clicker as clicker_module
from clicker import Clicker


class FakeWindowsInput:
    def __init__(self, fail=False):
        self.events = []
        self.fail = fail

    def key_down(self, key):
        if self.fail:
            raise OSError("blocked")
        self.events.append(("key_down", key))

    def key_up(self, key):
        self.events.append(("key_up", key))

    def mouse_down(self, button):
        self.events.append(("mouse_down", button))

    def mouse_up(self, button):
        self.events.append(("mouse_up", button))


def test_windows_keyboard_pulse(monkeypatch):
    clicker = Clicker()
    backend = FakeWindowsInput()
    clicker.controller = backend
    clicker.set_key("Shift_L")
    sleeps = []
    monkeypatch.setattr(clicker_module, "IS_WINDOWS", True)
    monkeypatch.setattr(clicker_module.time, "sleep", sleeps.append)

    press_time = clicker._emit_once()

    assert backend.events == [("key_down", "Shift_L"), ("key_up", "Shift_L")]
    assert sleeps == [press_time]
    assert press_time > 0


def test_windows_mouse_pulse(monkeypatch):
    clicker = Clicker()
    backend = FakeWindowsInput()
    clicker.controller = backend
    clicker.set_target("mouse")
    clicker.set_key("right")
    monkeypatch.setattr(clicker_module, "IS_WINDOWS", True)
    monkeypatch.setattr(clicker_module.time, "sleep", lambda _seconds: None)

    clicker._emit_once()

    assert backend.events == [("mouse_down", "right"), ("mouse_up", "right")]


def test_input_error_stops_loop(monkeypatch):
    clicker = Clicker()
    clicker.controller = FakeWindowsInput(fail=True)
    errors = []
    clicker.on_error = errors.append
    clicker.is_clicking = True
    monkeypatch.setattr(clicker_module, "IS_WINDOWS", True)

    clicker._click_loop()

    assert clicker.is_clicking is False
    assert errors == ["blocked"]
