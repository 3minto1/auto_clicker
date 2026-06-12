import json
import time
import threading
import ctypes
from ctypes import wintypes
from pynput import keyboard, mouse


class MacroManager:
    def __init__(self):
        self.is_recording = False
        self.is_playing = False
        self.recorded_actions = []
        self._last_event_time = 0
        self._keyboard_listener = None
        self._mouse_listener = None
        self._play_thread = None
        self._stop_event = threading.Event()
        self.on_record_start = None
        self.on_record_stop = None
        self.on_play_start = None
        self.on_play_stop = None

    def start_recording(self):
        if self.is_recording or self.is_playing:
            return
        self.recorded_actions = []
        self._last_event_time = time.time()
        self.is_recording = True

        try:
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self._keyboard_listener.daemon = True
            self._keyboard_listener.start()
        except Exception:
            pass

        try:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            self._mouse_listener.daemon = True
            self._mouse_listener.start()
        except Exception:
            pass

        time.sleep(0.1)

        if self.on_record_start:
            self.on_record_start()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        time.sleep(0.05)
        if self._keyboard_listener:
            try:
                self._keyboard_listener.stop()
            except Exception:
                pass
            self._keyboard_listener = None
        if self._mouse_listener:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass
            self._mouse_listener = None
        if self.on_record_stop:
            self.on_record_stop()

    def start_playback(self, actions=None):
        if self.is_playing or self.is_recording:
            return
        if actions is None:
            actions = self.recorded_actions
        if not actions:
            return

        self.is_playing = True
        self._stop_event.clear()
        self._play_thread = threading.Thread(target=self._play_loop, args=(actions,), daemon=True)
        self._play_thread.start()

        if self.on_play_start:
            self.on_play_start()

    def stop_playback(self):
        if not self.is_playing:
            return
        self._stop_event.set()
        self.is_playing = False
        if self.on_play_stop:
            self.on_play_stop()

    def _get_cursor_pos_win32(self):
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y

    def _set_cursor_pos_win32(self, x, y):
        ctypes.windll.user32.SetCursorPos(int(x), int(y))
        time.sleep(0.01)

    def _play_loop(self, actions):
        kb_controller = keyboard.Controller()
        ms_controller = mouse.Controller()

        for action in actions:
            if self._stop_event.is_set():
                break

            delay = action.get("delay", 0)
            if delay > 0:
                time.sleep(min(delay, 5.0))

            action_type = action["type"]

            try:
                if action_type == "key_press":
                    name = action.get("name", "")
                    key = self._resolve_key(name)
                    kb_controller.press(key)
                elif action_type == "key_release":
                    name = action.get("name", "")
                    key = self._resolve_key(name)
                    kb_controller.release(key)
                elif action_type == "mouse_click":
                    x = action.get("x", 0)
                    y = action.get("y", 0)
                    button_name = action.get("button", "left")
                    self._set_cursor_pos_win32(x, y)
                    btn = self._get_mouse_button(button_name)
                    ms_controller.click(btn)
                elif action_type == "mouse_press":
                    x = action.get("x", 0)
                    y = action.get("y", 0)
                    button_name = action.get("button", "left")
                    self._set_cursor_pos_win32(x, y)
                    btn = self._get_mouse_button(button_name)
                    ms_controller.press(btn)
                elif action_type == "mouse_release":
                    x = action.get("x", 0)
                    y = action.get("y", 0)
                    button_name = action.get("button", "left")
                    self._set_cursor_pos_win32(x, y)
                    btn = self._get_mouse_button(button_name)
                    ms_controller.release(btn)
                elif action_type == "mouse_scroll":
                    x = action.get("x", 0)
                    y = action.get("y", 0)
                    dy = action.get("dy", 0)
                    self._set_cursor_pos_win32(x, y)
                    ms_controller.scroll(0, dy)
            except Exception:
                pass

        self.is_playing = False
        if self.on_play_stop:
            self.on_play_stop()

    def _resolve_key(self, name):
        key_map = {
            "shift": keyboard.Key.shift,
            "shift_l": keyboard.Key.shift_l,
            "shift_r": keyboard.Key.shift_r,
            "ctrl": keyboard.Key.ctrl,
            "ctrl_l": keyboard.Key.ctrl_l,
            "ctrl_r": keyboard.Key.ctrl_r,
            "alt": keyboard.Key.alt,
            "alt_l": keyboard.Key.alt_l,
            "alt_r": keyboard.Key.alt_r,
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
        name_lower = name.lower()
        if name_lower in key_map:
            return key_map[name_lower]
        return name

    def _get_mouse_button(self, name):
        button_map = {
            "left": mouse.Button.left,
            "right": mouse.Button.right,
            "middle": mouse.Button.middle,
        }
        return button_map.get(name, mouse.Button.left)

    def _get_key_name(self, key):
        try:
            if hasattr(key, 'name'):
                return key.name
            if hasattr(key, 'char') and key.char:
                return key.char
            return str(key)
        except Exception:
            return str(key)

    def _on_key_press(self, key):
        if not self.is_recording:
            return
        now = time.time()
        delay = now - self._last_event_time
        self._last_event_time = now
        name = self._get_key_name(key)
        self.recorded_actions.append({
            "type": "key_press",
            "name": name,
            "delay": delay
        })

    def _on_key_release(self, key):
        if not self.is_recording:
            return
        now = time.time()
        delay = now - self._last_event_time
        self._last_event_time = now
        name = self._get_key_name(key)
        self.recorded_actions.append({
            "type": "key_release",
            "name": name,
            "delay": delay
        })

    def _on_mouse_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
        now = time.time()
        delay = now - self._last_event_time
        self._last_event_time = now

        try:
            real_x, real_y = self._get_cursor_pos_win32()
        except Exception:
            real_x, real_y = x, y

        action_type = "mouse_press" if pressed else "mouse_release"
        button_name = "left" if button == mouse.Button.left else ("right" if button == mouse.Button.right else "middle")
        self.recorded_actions.append({
            "type": action_type,
            "button": button_name,
            "x": real_x,
            "y": real_y,
            "delay": delay
        })

    def _on_mouse_scroll(self, x, y, dx, dy):
        if not self.is_recording:
            return
        now = time.time()
        delay = now - self._last_event_time
        self._last_event_time = now

        try:
            real_x, real_y = self._get_cursor_pos_win32()
        except Exception:
            real_x, real_y = x, y

        self.recorded_actions.append({
            "type": "mouse_scroll",
            "x": real_x,
            "y": real_y,
            "dx": dx,
            "dy": dy,
            "delay": delay
        })

    def save_macro(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.recorded_actions, f, indent=2)

    def load_macro(self, filepath):
        with open(filepath, 'r') as f:
            self.recorded_actions = json.load(f)

    def get_duration(self):
        if not self.recorded_actions:
            return 0
        return sum(a.get("delay", 0) for a in self.recorded_actions)

    def get_action_count(self):
        return len(self.recorded_actions)
