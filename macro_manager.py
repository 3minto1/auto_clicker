import json
import time
import threading
from pynput import keyboard, mouse


class MacroManager:
    def __init__(self):
        self.is_recording = False
        self.is_playing = False
        self.recorded_actions = []
        self._start_time = 0
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
        self._start_time = time.time()
        self.is_recording = True

        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._keyboard_listener.daemon = True
        self._keyboard_listener.start()

        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

        if self.on_record_start:
            self.on_record_start()

    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
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
        self._play_thread = threading.Thread(target=self._play_loop, args=(actions,))
        self._play_thread.daemon = True
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

    def _play_loop(self, actions):
        kb_controller = keyboard.Controller()
        ms_controller = mouse.Controller()

        for action in actions:
            if self._stop_event.is_set():
                break

            delay = action.get("delay", 0)
            if delay > 0:
                time.sleep(delay)

            action_type = action["type"]
            name = action.get("name", "")
            button = action.get("button", "")
            x = action.get("x", 0)
            y = action.get("y", 0)

            try:
                if action_type == "key_press":
                    kb_controller.press(name)
                elif action_type == "key_release":
                    kb_controller.release(name)
                elif action_type == "mouse_click":
                    ms_controller.position = (x, y)
                    btn = self._get_mouse_button(button)
                    ms_controller.click(btn)
                elif action_type == "mouse_press":
                    ms_controller.position = (x, y)
                    btn = self._get_mouse_button(button)
                    ms_controller.press(btn)
                elif action_type == "mouse_release":
                    ms_controller.position = (x, y)
                    btn = self._get_mouse_button(button)
                    ms_controller.release(btn)
                elif action_type == "mouse_scroll":
                    ms_controller.position = (x, y)
                    ms_controller.scroll(0, action.get("dy", 0))
            except Exception:
                pass

        self.is_playing = False
        if self.on_play_stop:
            self.on_play_stop()

    def _get_mouse_button(self, name):
        button_map = {
            "left": mouse.Button.left,
            "right": mouse.Button.right,
            "middle": mouse.Button.middle,
        }
        return button_map.get(name, mouse.Button.left)

    def _on_key_press(self, key):
        if not self.is_recording:
            return
        delay = time.time() - self._start_time
        self._start_time = time.time()
        name = key.name if hasattr(key, 'name') else (key.char if hasattr(key, 'char') and key.char else str(key))
        self.recorded_actions.append({
            "type": "key_press",
            "name": name,
            "delay": delay
        })

    def _on_key_release(self, key):
        if not self.is_recording:
            return
        delay = time.time() - self._start_time
        self._start_time = time.time()
        name = key.name if hasattr(key, 'name') else (key.char if hasattr(key, 'char') and key.char else str(key))
        self.recorded_actions.append({
            "type": "key_release",
            "name": name,
            "delay": delay
        })

    def _on_mouse_click(self, x, y, button, pressed):
        if not self.is_recording:
            return
        delay = time.time() - self._start_time
        self._start_time = time.time()
        action_type = "mouse_press" if pressed else "mouse_release"
        button_name = "left" if button == mouse.Button.left else ("right" if button == mouse.Button.right else "middle")
        self.recorded_actions.append({
            "type": action_type,
            "button": button_name,
            "x": x,
            "y": y,
            "delay": delay
        })

    def _on_mouse_scroll(self, x, y, dx, dy):
        if not self.is_recording:
            return
        delay = time.time() - self._start_time
        self._start_time = time.time()
        self.recorded_actions.append({
            "type": "mouse_scroll",
            "x": x,
            "y": y,
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
