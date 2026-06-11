import time
import threading
from pynput import keyboard, mouse

class Clicker:
    def __init__(self):
        self.target = "keyboard"
        self.key = "a"
        self.interval = 100
        self.is_clicking = False
        self.click_thread = None
        self.controller = None

    def set_target(self, target):
        if target in ["keyboard", "mouse"]:
            self.target = target

    def set_key(self, key):
        self.key = key

    def set_interval(self, interval):
        if 1 <= interval <= 1000:
            self.interval = interval

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

    def _click_loop(self):
        while self.is_clicking:
            if self.target == "keyboard":
                self.controller.press(self.key)
                self.controller.release(self.key)
            else:
                self.controller.click(mouse.Button.left)
            time.sleep(self.interval / 1000.0)
