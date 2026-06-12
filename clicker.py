import time
import threading
from pynput import keyboard, mouse


class Clicker:
    MODIFIER_MAP = {
        "shift": keyboard.Key.shift,
        "shift_l": keyboard.Key.shift_l,
        "shift_r": keyboard.Key.shift_r,
        "ctrl": keyboard.Key.ctrl,
        "ctrl_l": keyboard.Key.ctrl_l,
        "ctrl_r": keyboard.Key.ctrl_r,
        "alt": keyboard.Key.alt,
        "alt_l": keyboard.Key.alt_l,
        "alt_r": keyboard.Key.alt_r,
        "alt_gr": keyboard.Key.alt_gr,
        "cmd": keyboard.Key.cmd,
        "cmd_l": keyboard.Key.cmd_l,
        "cmd_r": keyboard.Key.cmd_r,
        "space": keyboard.Key.space,
        "enter": keyboard.Key.enter,
        "tab": keyboard.Key.tab,
        "backspace": keyboard.Key.backspace,
        "delete": keyboard.Key.delete,
        "esc": keyboard.Key.esc,
        "up": keyboard.Key.up,
        "down": keyboard.Key.down,
        "left": keyboard.Key.left,
        "right": keyboard.Key.right,
        "home": keyboard.Key.home,
        "end": keyboard.Key.end,
        "page_up": keyboard.Key.page_up,
        "page_down": keyboard.Key.page_down,
        "caps_lock": keyboard.Key.caps_lock,
        "f1": keyboard.Key.f1, "f2": keyboard.Key.f2,
        "f3": keyboard.Key.f3, "f4": keyboard.Key.f4,
        "f5": keyboard.Key.f5, "f6": keyboard.Key.f6,
        "f7": keyboard.Key.f7, "f8": keyboard.Key.f8,
        "f9": keyboard.Key.f9, "f10": keyboard.Key.f10,
        "f11": keyboard.Key.f11, "f12": keyboard.Key.f12,
    }

    MOUSE_BUTTON_MAP = {
        "left": mouse.Button.left,
        "right": mouse.Button.right,
        "middle": mouse.Button.middle,
        "button1": mouse.Button.left,
        "button2": mouse.Button.right,
        "button3": mouse.Button.middle,
    }

    def __init__(self):
        self.target = "keyboard"
        self.key = "a"
        self.interval = 100
        self.is_clicking = False
        self.click_thread = None
        self.controller = None
        self.click_count = 0
        self.max_clicks = 0
        self.on_click = None
        self.on_max_reached = None

    def set_target(self, target):
        if target in ["keyboard", "mouse"]:
            self.target = target

    def set_key(self, key):
        self.key = key

    def set_interval(self, interval):
        if 1 <= interval <= 1000:
            self.interval = interval

    def set_max_clicks(self, max_clicks):
        self.max_clicks = max(0, int(max_clicks))

    def reset_counter(self):
        self.click_count = 0

    def start_clicking(self):
        if self.is_clicking:
            return

        self.is_clicking = True
        if self.target == "keyboard":
            self.controller = keyboard.Controller()
        else:
            self.controller = mouse.Controller()

        self.click_thread = threading.Thread(target=self._click_loop)
        self.click_thread.start()

    def stop_clicking(self):
        self.is_clicking = False
        if self.click_thread:
            self.click_thread.join()

    def _resolve_key(self, key_name):
        key_lower = key_name.lower()
        if key_lower in self.MODIFIER_MAP:
            return self.MODIFIER_MAP[key_lower]
        return key_name

    def _click_loop(self):
        while self.is_clicking:
            if self.target == "keyboard":
                key = self._resolve_key(self.key)
                self.controller.press(key)
                self.controller.release(key)
            else:
                button = self.MOUSE_BUTTON_MAP.get(self.key.lower(), mouse.Button.left)
                self.controller.click(button)

            self.click_count += 1
            if self.on_click:
                self.on_click(self.click_count)

            if self.max_clicks > 0 and self.click_count >= self.max_clicks:
                self.is_clicking = False
                if self.on_max_reached:
                    self.on_max_reached()
                break

            time.sleep(self.interval / 1000.0)
