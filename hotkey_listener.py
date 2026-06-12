import threading
from pynput import keyboard


class HotkeyListener:
    def __init__(self):
        self.current_hotkey = "F6"
        self.mode = "toggle"
        self.is_listening = False
        self.callback = None
        self._listener = None
        self._hotkey_pressed = False

    def set_hotkey(self, hotkey):
        self.current_hotkey = hotkey

    def set_mode(self, mode):
        if mode in ["toggle", "hold"]:
            self.mode = mode

    def start_listening(self, callback):
        self.callback = callback
        self.is_listening = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.daemon = True
        self._listener.start()

    def stop_listening(self):
        self.is_listening = False
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _on_press(self, key):
        if not self.is_listening:
            return
        key_name = self._get_key_name(key).lower()
        if key_name == self.current_hotkey.lower():
            if self.mode == "toggle" and not self._hotkey_pressed:
                self._hotkey_pressed = True
                if self.callback:
                    self.callback()
            elif self.mode == "hold" and not self._hotkey_pressed:
                self._hotkey_pressed = True
                if self.callback:
                    self.callback()

    def _on_release(self, key):
        if not self.is_listening:
            return
        key_name = self._get_key_name(key).lower()
        if key_name == self.current_hotkey.lower():
            self._hotkey_pressed = False
            if self.mode == "hold" and self.callback:
                self.callback()

    def _get_key_name(self, key):
        if hasattr(key, 'name'):
            return key.name
        if hasattr(key, 'char') and key.char:
            return key.char.upper()
        return str(key)
