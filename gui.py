import tkinter as tk
from tkinter import ttk
from config_manager import ConfigManager
from hotkey_listener import HotkeyListener
from clicker import Clicker

class AutoClickerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("连点器")
        self.root.geometry("400x300")
        
        self.config_manager = ConfigManager()
        self.hotkey_listener = HotkeyListener()
        self.clicker = Clicker()
        
        self.hotkey_var = tk.StringVar(value="F6")
        self.mode_var = tk.StringVar(value="toggle")
        self.interval_var = tk.IntVar(value=100)
        self.target_var = tk.StringVar(value="keyboard")
        self.key_var = tk.StringVar(value="a")
        
        self.create_widgets()
        self.load_config()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="启动热键:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.hotkey_var, width=10).grid(row=0, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="设置热键", command=self.set_hotkey).grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(main_frame, text="启动模式:").grid(row=1, column=0, sticky=tk.W)
        ttk.Combobox(main_frame, textvariable=self.mode_var, values=["toggle", "hold"], state="readonly").grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(main_frame, text="点击间隔(ms):").grid(row=2, column=0, sticky=tk.W)
        ttk.Spinbox(main_frame, from_=1, to=1000, textvariable=self.interval_var, width=10).grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(main_frame, text="模拟目标:").grid(row=3, column=0, sticky=tk.W)
        ttk.Combobox(main_frame, textvariable=self.target_var, values=["keyboard", "mouse"], state="readonly").grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(main_frame, text="模拟按键:").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.key_var, width=10).grid(row=4, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="设置按键", command=self.set_key).grid(row=4, column=2, sticky=tk.W)
        
        self.start_button = ttk.Button(main_frame, text="开始", command=self.toggle_clicking)
        self.start_button.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E)
        
        self.status_label = ttk.Label(main_frame, text="状态: 停止")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W)
    
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
    
    def set_hotkey(self):
        self.status_label.config(text="状态: 请按下新热键...")
        self.root.bind("<KeyPress>", self.on_hotkey_pressed)
    
    def on_hotkey_pressed(self, event):
        self.hotkey_var.set(event.keysym)
        self.root.unbind("<KeyPress>")
        self.status_label.config(text="状态: 停止")
        self.save_config()
    
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
        button_map = {
            1: "left",
            2: "middle",
            3: "right"
        }
        button_name = button_map.get(event.num, "left")
        self.key_var.set(button_name)
        self.root.unbind("<ButtonPress-1>")
        self.root.unbind("<ButtonPress-2>")
        self.root.unbind("<ButtonPress-3>")
        self.status_label.config(text="状态: 停止")
        self.save_config()
    
    def toggle_clicking(self):
        if self.clicker.is_clicking:
            self.clicker.stop_clicking()
            self.start_button.config(text="开始")
            self.status_label.config(text="状态: 停止")
        else:
            self.save_config()
            self.clicker.set_target(self.target_var.get())
            self.clicker.set_key(self.key_var.get())
            self.clicker.set_interval(self.interval_var.get())
            self.clicker.start_clicking()
            self.start_button.config(text="停止")
            self.status_label.config(text="状态: 运行中")
    
    def run(self):
        self.root.mainloop()