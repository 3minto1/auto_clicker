import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from config_manager import ConfigManager
from hotkey_listener import HotkeyListener
from clicker import Clicker


class AutoClickerGUI:
    BASE_WIDTH = 400
    BASE_HEIGHT = 300
    BASE_FONT_SIZE = 10

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("连点器")
        self.root.geometry(f"{self.BASE_WIDTH}x{self.BASE_HEIGHT}")
        self.root.minsize(250, 200)

        self.config_manager = ConfigManager()
        self.hotkey_listener = HotkeyListener()
        self.clicker = Clicker()
        self._running = False
        self._scale = 1.0
        self._widgets = []

        self.hotkey_var = tk.StringVar(value="F6")
        self.mode_var = tk.StringVar(value="toggle")
        self.interval_var = tk.IntVar(value=100)
        self.target_var = tk.StringVar(value="keyboard")
        self.key_var = tk.StringVar(value="a")

        self._init_fonts()
        self.create_widgets()
        self.load_config()
        self._start_hotkey_listener()

        self.root.bind("<Configure>", self._on_resize)

    def _init_fonts(self):
        self.default_font = tkfont.nametofont("TkDefaultFont")
        self.default_font.configure(size=self.BASE_FONT_SIZE)
        self.entry_font = tkfont.Font(family=self.default_font.cget("family"), size=self.BASE_FONT_SIZE)
        self.button_font = tkfont.Font(family=self.default_font.cget("family"), size=self.BASE_FONT_SIZE)
        self.bold_font = tkfont.Font(family=self.default_font.cget("family"), size=self.BASE_FONT_SIZE, weight="bold")

    def _on_resize(self, event):
        if event.widget != self.root:
            return
        new_scale = event.width / self.BASE_WIDTH
        if abs(new_scale - self._scale) < 0.05:
            return
        self._scale = new_scale
        new_size = max(8, int(self.BASE_FONT_SIZE * self._scale))

        self.default_font.configure(size=new_size)
        self.entry_font.configure(size=new_size)
        self.button_font.configure(size=new_size)
        self.bold_font.configure(size=new_size)

        pad = max(4, int(10 * self._scale))
        self.main_frame.configure(padding=f"{pad}")

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        rows = [
            ("启动热键:", self.hotkey_var, "Entry", "设置热键", self.set_hotkey),
            ("启动模式:", self.mode_var, "Combobox", None, None),
            ("点击间隔(ms):", self.interval_var, "Spinbox", None, None),
            ("模拟目标:", self.target_var, "Combobox", None, None),
            ("模拟按键:", self.key_var, "Entry", "设置按键", self.set_key),
        ]

        for i, (label_text, var, widget_type, btn_text, btn_cmd) in enumerate(rows):
            lbl = ttk.Label(self.main_frame, text=label_text, font=self.default_font)
            lbl.grid(row=i, column=0, sticky=tk.W, pady=2)
            self._widgets.append(lbl)

            if widget_type == "Entry":
                w = ttk.Entry(self.main_frame, textvariable=var, width=12, font=self.entry_font)
            elif widget_type == "Combobox":
                values = ["toggle", "hold"] if label_text == "启动模式:" else ["keyboard", "mouse"]
                w = ttk.Combobox(self.main_frame, textvariable=var, values=values, state="readonly", font=self.entry_font)
            elif widget_type == "Spinbox":
                w = ttk.Spinbox(self.main_frame, from_=1, to=1000, textvariable=var, width=12, font=self.entry_font)
            w.grid(row=i, column=1, sticky=tk.W, pady=2)
            self._widgets.append(w)

            if btn_text:
                btn = ttk.Button(self.main_frame, text=btn_text, command=btn_cmd)
                btn.grid(row=i, column=2, sticky=tk.W, padx=(5, 0), pady=2)
                self._widgets.append(btn)

        self.start_button = ttk.Button(self.main_frame, text="开始", command=self.toggle_clicking)
        self.start_button.grid(row=5, column=0, columnspan=3, sticky=tk.W + tk.E, pady=(8, 2))
        self._widgets.append(self.start_button)

        self.status_label = ttk.Label(self.main_frame, text="状态: 停止", font=self.bold_font)
        self.status_label.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=2)
        self._widgets.append(self.status_label)

    def load_config(self):
        config = self.config_manager.load_config()
        self.hotkey_var.set(config.get("hotkey", "F6"))
        self.mode_var.set(config.get("mode", "toggle"))
        self.interval_var.set(config.get("interval", 100))
        self.target_var.set(config.get("target", "keyboard"))
        self.key_var.set(config.get("key", "a"))

    def save_config(self):
        config = {
            "hotkey": self.hotkey_var.get(),
            "mode": self.mode_var.get(),
            "interval": self.interval_var.get(),
            "target": self.target_var.get(),
            "key": self.key_var.get()
        }
        self.config_manager.save_config(config)

    def _start_hotkey_listener(self):
        self.hotkey_listener.set_hotkey(self.hotkey_var.get())
        self.hotkey_listener.set_mode(self.mode_var.get())
        self.hotkey_listener.start_listening(self._on_hotkey_triggered)

    def _on_hotkey_triggered(self):
        self.root.after(0, self.toggle_clicking)

    def set_hotkey(self):
        self.status_label.config(text="状态: 请按下新热键...")
        self.root.bind("<KeyPress>", self.on_hotkey_pressed)

    def on_hotkey_pressed(self, event):
        new_hotkey = event.keysym
        self.hotkey_var.set(new_hotkey)
        self.root.unbind("<KeyPress>")
        self.status_label.config(text="状态: 停止")
        self.save_config()
        self.hotkey_listener.set_hotkey(new_hotkey)

    def set_key(self):
        self.status_label.config(text="状态: 请按下新按键...")
        target = self.target_var.get()
        if target == "keyboard":
            self.root.bind("<KeyPress>", self.on_key_pressed)
        else:
            self.root.bind("<ButtonPress-1>", self.on_mouse_button_pressed)
            self.root.bind("<ButtonPress-2>", self.on_mouse_button_pressed)
            self.root.bind("<ButtonPress-3>", self.on_mouse_button_pressed)

    def on_key_pressed(self, event):
        self.key_var.set(event.keysym)
        self.root.unbind("<KeyPress>")
        self.status_label.config(text="状态: 停止")
        self.save_config()

    def on_mouse_button_pressed(self, event):
        button_map = {1: "left", 2: "middle", 3: "right"}
        button_name = button_map.get(event.num, "left")
        self.key_var.set(button_name)
        self.root.unbind("<ButtonPress-1>")
        self.root.unbind("<ButtonPress-2>")
        self.root.unbind("<ButtonPress-3>")
        self.status_label.config(text="状态: 停止")
        self.save_config()

    def toggle_clicking(self):
        if self._running:
            self.clicker.stop_clicking()
            self._running = False
            self.start_button.config(text="开始")
            self.status_label.config(text="状态: 停止")
        else:
            self.save_config()
            self.hotkey_listener.set_hotkey(self.hotkey_var.get())
            self.hotkey_listener.set_mode(self.mode_var.get())
            self.clicker.set_target(self.target_var.get())
            self.clicker.set_key(self.key_var.get())
            self.clicker.set_interval(self.interval_var.get())
            self.clicker.start_clicking()
            self._running = True
            self.start_button.config(text="停止")
            self.status_label.config(text="状态: 运行中")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self.hotkey_listener.stop_listening()
        if self._running:
            self.clicker.stop_clicking()
        self.root.destroy()
