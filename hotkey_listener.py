import threading
import time
from pynput import keyboard

from windows_input import IS_WINDOWS, hotkey_to_vks, is_vk_down


class HotkeyListener:
    def __init__(self):
        self.current_hotkey = "F6"
        self.mode = "toggle"
        self.is_listening = False
        self.callback = None
        self._listener = None
        self._hotkey_pressed = False
        self._hotkey_vks = []

    def set_hotkey(self, hotkey):
        self.current_hotkey = hotkey
        if IS_WINDOWS:
            self._hotkey_vks = hotkey_to_vks(hotkey)

    def set_mode(self, mode):
        if mode in ["toggle", "hold"]:
            self.mode = mode

    def start_listening(self, callback):
        self.stop_listening()
        self.callback = callback
        self.is_listening = True
        if IS_WINDOWS:
            self._hotkey_vks = hotkey_to_vks(self.current_hotkey)
            self._listener = threading.Thread(target=self._poll_hotkey, daemon=True)
            self._listener.start()
            return
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.daemon = True
        self._listener.start()

    def stop_listening(self):
        self.is_listening = False
        if self._listener:
            if IS_WINDOWS:
                if self._listener is not threading.current_thread():
                    self._listener.join(timeout=0.2)
            else:
                self._listener.stop()
            self._listener = None
        self._hotkey_pressed = False

    def _poll_hotkey(self):
        while self.is_listening:
            try:
                pressed = bool(self._hotkey_vks) and all(is_vk_down(vk) for vk in self._hotkey_vks)
                if pressed and not self._hotkey_pressed:
                    self._hotkey_pressed = True
                    if self.callback:
                        self.callback()
                elif not pressed and self._hotkey_pressed:
                    self._hotkey_pressed = False
                    if self.mode == "hold" and self.callback:
                        self.callback()
            except Exception:
                pass
            time.sleep(0.01)

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
