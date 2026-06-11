from pynput import keyboard


class HotkeyListener:
    def __init__(self):
        self.current_hotkey = "F6"
        self.mode = "toggle"
        self.is_listening = False
        self.callback = None

    def set_hotkey(self, hotkey):
        self.current_hotkey = hotkey

    def set_mode(self, mode):
        if mode in ["toggle", "hold"]:
            self.mode = mode

    def start_listening(self, callback):
        self.callback = callback
        self.is_listening = True

    def stop_listening(self):
        self.is_listening = False
