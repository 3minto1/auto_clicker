import ctypes
import sys
from ctypes import wintypes


IS_WINDOWS = sys.platform == "win32"


if IS_WINDOWS:
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    ULONG_PTR = wintypes.WPARAM

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = (
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        )

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = (
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        )

    class INPUT_UNION(ctypes.Union):
        _fields_ = (("mi", MOUSEINPUT), ("ki", KEYBDINPUT))

    class INPUT(ctypes.Structure):
        _anonymous_ = ("value",)
        _fields_ = (("type", wintypes.DWORD), ("value", INPUT_UNION))

    user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
    user32.SendInput.restype = wintypes.UINT
    user32.GetAsyncKeyState.argtypes = (ctypes.c_int,)
    user32.GetAsyncKeyState.restype = wintypes.SHORT
    user32.MapVirtualKeyW.argtypes = (wintypes.UINT, wintypes.UINT)
    user32.MapVirtualKeyW.restype = wintypes.UINT
    user32.VkKeyScanW.argtypes = (wintypes.WCHAR,)
    user32.VkKeyScanW.restype = wintypes.SHORT


VK_ALIASES = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "return": 0x0D,
    "shift": 0x10,
    "shift_l": 0xA0,
    "shift_r": 0xA1,
    "ctrl": 0x11,
    "control": 0x11,
    "ctrl_l": 0xA2,
    "control_l": 0xA2,
    "ctrl_r": 0xA3,
    "control_r": 0xA3,
    "alt": 0x12,
    "alt_l": 0xA4,
    "alt_r": 0xA5,
    "alt_gr": 0xA5,
    "pause": 0x13,
    "caps_lock": 0x14,
    "esc": 0x1B,
    "escape": 0x1B,
    "space": 0x20,
    "page_up": 0x21,
    "prior": 0x21,
    "page_down": 0x22,
    "next": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "insert": 0x2D,
    "delete": 0x2E,
    "cmd": 0x5B,
    "cmd_l": 0x5B,
    "cmd_r": 0x5C,
    "win": 0x5B,
    "win_l": 0x5B,
    "win_r": 0x5C,
}

EXTENDED_VKS = {
    0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28,
    0x2D, 0x2E, 0x5B, 0x5C, 0xA3, 0xA5,
}

MOUSE_FLAGS = {
    "left": (0x0002, 0x0004, 0),
    "button1": (0x0002, 0x0004, 0),
    "right": (0x0008, 0x0010, 0),
    "button2": (0x0008, 0x0010, 0),
    "middle": (0x0020, 0x0040, 0),
    "button3": (0x0020, 0x0040, 0),
}


def key_name_to_vk(key_name):
    name = str(key_name).strip().lower()
    if name in VK_ALIASES:
        return VK_ALIASES[name]
    if name.startswith("f") and name[1:].isdigit():
        number = int(name[1:])
        if 1 <= number <= 24:
            return 0x6F + number
    if len(name) == 1 and IS_WINDOWS:
        result = user32.VkKeyScanW(name)
        if result != -1:
            return result & 0xFF
    if len(name) == 1:
        return ord(name.upper())
    raise ValueError(f"Unsupported key: {key_name}")


def hotkey_to_vks(hotkey):
    return [key_name_to_vk(part) for part in str(hotkey).split("+") if part.strip()]


class WindowsInput:
    INPUT_MOUSE = 0
    INPUT_KEYBOARD = 1
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_SCANCODE = 0x0008
    MAPVK_VK_TO_VSC = 0

    def _send(self, input_event):
        sent = user32.SendInput(1, ctypes.byref(input_event), ctypes.sizeof(INPUT))
        if sent != 1:
            error = ctypes.get_last_error()
            detail = f"Win32 error {error}" if error else "input was blocked"
            raise OSError(f"SendInput failed: {detail}")

    def key_down(self, key_name):
        self._send_key(key_name_to_vk(key_name), is_key_up=False)

    def key_up(self, key_name):
        self._send_key(key_name_to_vk(key_name), is_key_up=True)

    def _send_key(self, vk, is_key_up):
        scan_code = user32.MapVirtualKeyW(vk, self.MAPVK_VK_TO_VSC)
        if not scan_code:
            raise ValueError(f"No scan code for virtual key 0x{vk:02X}")
        flags = self.KEYEVENTF_SCANCODE
        if vk in EXTENDED_VKS:
            flags |= self.KEYEVENTF_EXTENDEDKEY
        if is_key_up:
            flags |= self.KEYEVENTF_KEYUP
        event = INPUT(
            type=self.INPUT_KEYBOARD,
            ki=KEYBDINPUT(wVk=0, wScan=scan_code, dwFlags=flags, time=0, dwExtraInfo=0),
        )
        self._send(event)

    def mouse_down(self, button_name):
        self._send_mouse(button_name, release=False)

    def mouse_up(self, button_name):
        self._send_mouse(button_name, release=True)

    def _send_mouse(self, button_name, release):
        down_flag, up_flag, data = MOUSE_FLAGS.get(str(button_name).lower(), MOUSE_FLAGS["left"])
        event = INPUT(
            type=self.INPUT_MOUSE,
            mi=MOUSEINPUT(
                dx=0,
                dy=0,
                mouseData=data,
                dwFlags=up_flag if release else down_flag,
                time=0,
                dwExtraInfo=0,
            ),
        )
        self._send(event)


def is_vk_down(vk):
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)
