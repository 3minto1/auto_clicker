import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from tkinter import filedialog
import threading
import pystray
from PIL import Image, ImageDraw
from config_manager import ConfigManager
from hotkey_listener import HotkeyListener
from clicker import Clicker
from macro_manager import MacroManager
from preset_manager import PresetManager


class AutoClickerGUI:
    BASE_WIDTH = 600
    BASE_HEIGHT = 500
    BASE_FONT_SIZE = 10

    BG_COLOR = "#f0f0f0"
    ACCENT_COLOR = "#4a90d9"
    ACCENT_HOVER = "#357abd"
    STOP_COLOR = "#e74c3c"
    STOP_HOVER = "#c0392b"
    RUNNING_COLOR = "#27ae60"
    RECORD_COLOR = "#e67e22"
    RECORD_HOVER = "#d35400"
    CARD_BG = "#ffffff"
    TEXT_COLOR = "#333333"
    LABEL_COLOR = "#555555"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("连点器")
        self.root.geometry(f"{self.BASE_WIDTH}x{self.BASE_HEIGHT}")
        self.root.minsize(500, 400)
        self.root.configure(bg=self.BG_COLOR)

        self.config_manager = ConfigManager()
        self.hotkey_listener = HotkeyListener()
        self.clicker = Clicker()
        self.macro_manager = MacroManager()
        self.preset_manager = PresetManager()
        self._running = False
        self._scale = 1.0
        self._tray_icon = None
        self._timer_job = None

        self.hotkey_var = tk.StringVar(value="F6")
        self.mode_var = tk.StringVar(value="toggle")
        self.interval_var = tk.IntVar(value=100)
        self.target_var = tk.StringVar(value="keyboard")
        self.key_var = tk.StringVar(value="a")
        self.close_to_tray_var = tk.BooleanVar(value=True)
        self.macro_status_var = tk.StringVar(value="未录制")
        self.macro_file_var = tk.StringVar(value="")
        self.max_clicks_var = tk.IntVar(value=0)
        self.click_count_var = tk.StringVar(value="0")
        self.max_seconds_var = tk.IntVar(value=0)
        self.elapsed_time_var = tk.StringVar(value="00:00")
        self.random_enabled_var = tk.BooleanVar(value=False)
        self.random_range_var = tk.IntVar(value=50)
        self.preset_name_var = tk.StringVar(value="")
        self.selected_preset_var = tk.StringVar(value="")

        self._init_fonts()
        self._init_styles()
        self._setup_macro_callbacks()
        self._setup_clicker_callbacks()
        self.create_widgets()
        self.load_config()
        self._start_hotkey_listener()

        self.root.bind("<Configure>", self._on_resize)

    def _init_fonts(self):
        base = tkfont.nametofont("TkDefaultFont")
        self.font_title = tkfont.Font(family=base.cget("family"), size=max(12, self.BASE_FONT_SIZE + 2), weight="bold")
        self.font_label = tkfont.Font(family=base.cget("family"), size=self.BASE_FONT_SIZE)
        self.font_entry = tkfont.Font(family=base.cget("family"), size=self.BASE_FONT_SIZE)
        self.font_button = tkfont.Font(family=base.cget("family"), size=self.BASE_FONT_SIZE, weight="bold")
        self.font_status = tkfont.Font(family=base.cget("family"), size=self.BASE_FONT_SIZE, weight="bold")
        self.font_small = tkfont.Font(family=base.cget("family"), size=max(8, self.BASE_FONT_SIZE - 1))

    def _init_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Card.TFrame", background=self.CARD_BG, relief="flat")
        style.configure("Card.TLabel", background=self.CARD_BG, foreground=self.TEXT_COLOR)
        style.configure("Title.TLabel", background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=self.font_title)
        style.configure("Status.TLabel", background=self.CARD_BG, foreground=self.LABEL_COLOR, font=self.font_status)
        style.configure("Running.TLabel", background=self.CARD_BG, foreground=self.RUNNING_COLOR, font=self.font_status)
        style.configure("Recording.TLabel", background=self.CARD_BG, foreground=self.RECORD_COLOR, font=self.font_status)
        style.configure("Hint.TLabel", background=self.CARD_BG, foreground="#999999", font=self.font_small)

        style.configure("Accent.TButton", font=self.font_button, padding=(12, 6))
        style.map("Accent.TButton",
                   background=[("active", self.ACCENT_HOVER), ("!active", self.ACCENT_COLOR)],
                   foreground=[("active", "white"), ("!active", "white")])

        style.configure("Stop.TButton", font=self.font_button, padding=(12, 6))
        style.map("Stop.TButton",
                   background=[("active", self.STOP_HOVER), ("!active", self.STOP_COLOR)],
                   foreground=[("active", "white"), ("!active", "white")])

        style.configure("Record.TButton", font=self.font_button, padding=(12, 6))
        style.map("Record.TButton",
                   background=[("active", self.RECORD_HOVER), ("!active", self.RECORD_COLOR)],
                   foreground=[("active", "white"), ("!active", "white")])

        style.configure("Set.TButton", font=self.font_label, padding=(6, 2))
        style.map("Set.TButton",
                   background=[("active", "#e0e0e0"), ("!active", "#e8e8e8")])

        style.configure("TEntry", font=self.font_entry, padding=4)
        style.configure("TCombobox", font=self.font_entry, padding=4)
        style.configure("TSpinbox", font=self.font_entry, padding=4)
        style.configure("TCheckbutton", background=self.CARD_BG, foreground=self.TEXT_COLOR)

    def _setup_macro_callbacks(self):
        self.macro_manager.on_record_start = self._on_macro_record_start
        self.macro_manager.on_record_stop = self._on_macro_record_stop
        self.macro_manager.on_play_start = self._on_macro_play_start
        self.macro_manager.on_play_stop = self._on_macro_play_stop

    def _setup_clicker_callbacks(self):
        self.clicker.on_click = self._on_click
        self.clicker.on_max_reached = self._on_max_reached
        self.clicker.on_timeout = self._on_timeout

    def _on_click(self, count):
        self.root.after(0, lambda: self.click_count_var.set(str(count)))

    def _on_max_reached(self):
        self.root.after(0, self._handle_stop)

    def _on_timeout(self):
        self.root.after(0, self._handle_stop)

    def _handle_stop(self):
        self._running = False
        self._stop_timer()
        self.start_button.configure(text="▶  开始", bg=self.ACCENT_COLOR)
        self.start_button.unbind("<Enter>")
        self.start_button.unbind("<Leave>")
        self.start_button.bind("<Enter>", lambda e: self.start_button.configure(bg=self.ACCENT_HOVER))
        self.start_button.bind("<Leave>", lambda e: self.start_button.configure(bg=self.ACCENT_COLOR))
        self._update_status_stopped()

    def _start_timer(self):
        if self._timer_job:
            self.root.after_cancel(self._timer_job)
        self._update_elapsed_time()

    def _stop_timer(self):
        if self._timer_job:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None

    def _update_elapsed_time(self):
        if not self._running:
            return
        elapsed = self.clicker.get_elapsed_time()
        minutes = int(elapsed) // 60
        seconds = int(elapsed) % 60
        self.elapsed_time_var.set(f"{minutes:02d}:{seconds:02d}")
        self._timer_job = self.root.after(1000, self._update_elapsed_time)

    def _on_resize(self, event):
        if event.widget != self.root:
            return
        new_scale = event.width / self.BASE_WIDTH
        if abs(new_scale - self._scale) < 0.05:
            return
        self._scale = new_scale

        sz = max(8, int(self.BASE_FONT_SIZE * self._scale))
        self.font_title.configure(size=max(12, sz + 2))
        self.font_label.configure(size=sz)
        self.font_entry.configure(size=sz)
        self.font_button.configure(size=sz)
        self.font_status.configure(size=sz)
        self.font_small.configure(size=max(8, sz - 1))

    def create_widgets(self):
        header = tk.Frame(self.root, bg=self.BG_COLOR)
        header.pack(fill=tk.X, padx=12, pady=(10, 5))

        ttk.Label(header, text="⚡ 连点器", style="Title.TLabel").pack(side=tk.LEFT)
        self.status_label = ttk.Label(header, text="● 已停止", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=(15, 0))

        main_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        left_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
        left_frame.columnconfigure(0, weight=1)

        right_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 6))
        right_frame.columnconfigure(0, weight=1)

        self._create_hotkey_card(left_frame, row=0)
        self._create_settings_card(left_frame, row=1)
        self._create_counter_card(left_frame, row=2)

        self._create_preset_card(right_frame, row=0)
        self._create_timer_card(right_frame, row=1)
        self._create_macro_card(right_frame, row=2)

        bottom_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        bottom_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        self._create_behavior_card(bottom_frame, col=0)
        self._create_action_card(bottom_frame, col=1)

    def _create_hotkey_card(self, parent, row):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 6))
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="启动热键", style="Card.TLabel", font=self.font_button).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(8, 4))

        ttk.Label(card, text="按键:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        self.hotkey_entry = ttk.Entry(card, textvariable=self.hotkey_var, width=10, justify="center")
        self.hotkey_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Button(card, text="设置", style="Set.TButton", command=self.set_hotkey).grid(
            row=1, column=2, sticky=tk.W, padx=(6, 10), pady=2)

        ttk.Label(card, text="模式:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Combobox(card, textvariable=self.mode_var, values=["toggle", "hold"],
                     state="readonly", width=8).grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Label(card, text="点按/长按", style="Hint.TLabel").grid(
            row=2, column=2, sticky=tk.W, padx=(6, 10), pady=2)

    def _create_settings_card(self, parent, row):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 6))
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="模拟设置", style="Card.TLabel", font=self.font_button).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(8, 4))

        ttk.Label(card, text="目标:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Combobox(card, textvariable=self.target_var, values=["keyboard", "mouse"],
                     state="readonly", width=8).grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(card, text="按键:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        self.key_entry = ttk.Entry(card, textvariable=self.key_var, width=10, justify="center")
        self.key_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Button(card, text="设置", style="Set.TButton", command=self.set_key).grid(
            row=2, column=2, sticky=tk.W, padx=(6, 10), pady=2)

        ttk.Label(card, text="间隔:", style="Card.TLabel").grid(row=3, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Spinbox(card, from_=1, to=1000, textvariable=self.interval_var, width=8).grid(
            row=3, column=1, sticky=tk.W, pady=2)
        ttk.Label(card, text="ms", style="Hint.TLabel").grid(
            row=3, column=2, sticky=tk.W, padx=(6, 10), pady=2)

        ttk.Checkbutton(card, text="随机间隔", variable=self.random_enabled_var,
                        style="TCheckbutton").grid(row=4, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Spinbox(card, from_=0, to=500, textvariable=self.random_range_var, width=8).grid(
            row=4, column=1, sticky=tk.W, pady=2)
        ttk.Label(card, text="±ms", style="Hint.TLabel").grid(
            row=4, column=2, sticky=tk.W, padx=(6, 10), pady=2)

    def _create_counter_card(self, parent, row):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=row, column=0, sticky="nsew")
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="点击计数", style="Card.TLabel", font=self.font_button).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(8, 4))

        ttk.Label(card, text="已点击:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Label(card, textvariable=self.click_count_var, style="Card.TLabel",
                  font=self.font_button).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Button(card, text="重置", style="Set.TButton", command=self.reset_counter).grid(
            row=1, column=2, sticky=tk.W, padx=(6, 10), pady=2)

        ttk.Label(card, text="最大次数:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Spinbox(card, from_=0, to=999999, textvariable=self.max_clicks_var, width=8).grid(
            row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(card, text="0=无限", style="Hint.TLabel").grid(
            row=2, column=2, sticky=tk.W, padx=(6, 10), pady=(2, 8))

    def _create_preset_card(self, parent, row):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 6))
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="配置预设", style="Card.TLabel", font=self.font_button).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(8, 4))

        ttk.Label(card, text="预设:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        self.preset_combo = ttk.Combobox(card, textvariable=self.selected_preset_var,
                                         values=self.preset_manager.get_preset_names(), width=10)
        self.preset_combo.grid(row=1, column=1, sticky=tk.W, pady=2)

        btn_frame = tk.Frame(card, bg=self.CARD_BG)
        btn_frame.grid(row=1, column=2, sticky=tk.W, padx=(6, 10), pady=2)
        ttk.Button(btn_frame, text="加载", style="Set.TButton", command=self.load_preset).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(btn_frame, text="删除", style="Set.TButton", command=self.delete_preset).pack(side=tk.LEFT)

        ttk.Label(card, text="名称:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Entry(card, textvariable=self.preset_name_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Button(card, text="保存", style="Set.TButton", command=self.save_preset).grid(
            row=2, column=2, sticky=tk.W, padx=(6, 10), pady=2)

        ttk.Label(card, text="快速切换配置", style="Hint.TLabel").grid(
            row=3, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(0, 8))

    def _create_timer_card(self, parent, row):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 6))
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="定时停止", style="Card.TLabel", font=self.font_button).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(8, 4))

        ttk.Label(card, text="已运行:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Label(card, textvariable=self.elapsed_time_var, style="Card.TLabel",
                  font=self.font_button).grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(card, text="最大时长:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Spinbox(card, from_=0, to=86400, textvariable=self.max_seconds_var, width=8).grid(
            row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(card, text="秒 0=无限", style="Hint.TLabel").grid(
            row=2, column=2, sticky=tk.W, padx=(6, 10), pady=(2, 8))

    def _create_macro_card(self, parent, row):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=row, column=0, sticky="nsew")
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="宏录制/回放", style="Card.TLabel", font=self.font_button).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=10, pady=(8, 4))

        btn_frame = tk.Frame(card, bg=self.CARD_BG)
        btn_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=10, pady=2)

        self.record_button = tk.Button(
            btn_frame, text="● 录制", font=self.font_button,
            bg=self.RECORD_COLOR, fg="white", activebackground=self.RECORD_HOVER,
            activeforeground="white", relief="flat", cursor="hand2",
            command=self.toggle_recording, width=8
        )
        self.record_button.pack(side=tk.LEFT, padx=(0, 5))

        self.play_button = tk.Button(
            btn_frame, text="▶ 回放", font=self.font_button,
            bg=self.ACCENT_COLOR, fg="white", activebackground=self.ACCENT_HOVER,
            activeforeground="white", relief="flat", cursor="hand2",
            command=self.toggle_playback, width=8
        )
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(btn_frame, text="保存", style="Set.TButton", command=self.save_macro).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(btn_frame, text="加载", style="Set.TButton", command=self.load_macro).pack(side=tk.LEFT)

        ttk.Label(card, text="状态:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Label(card, textvariable=self.macro_status_var, style="Card.TLabel").grid(
            row=2, column=1, columnspan=2, sticky=tk.W, pady=2)

        ttk.Label(card, text="文件:", style="Card.TLabel").grid(row=3, column=0, sticky=tk.W, padx=(10, 4), pady=2)
        ttk.Label(card, textvariable=self.macro_file_var, style="Hint.TLabel", wraplength=200).grid(
            row=3, column=1, columnspan=2, sticky=tk.W, pady=(2, 8))

    def _create_behavior_card(self, parent, col):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=(0, 6))

        ttk.Label(card, text="关闭行为", style="Card.TLabel", font=self.font_button).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=(8, 4))

        check = ttk.Checkbutton(card, text="最小化到托盘",
                                variable=self.close_to_tray_var, style="TCheckbutton",
                                command=self._on_close_to_tray_changed)
        check.grid(row=1, column=0, sticky=tk.W, padx=10, pady=(0, 8))

    def _create_action_card(self, parent, col):
        card = tk.Frame(parent, bg=self.CARD_BG, highlightbackground="#e0e0e0", highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=(6, 0))
        card.columnconfigure(0, weight=1)

        self.start_button = tk.Button(
            card, text="▶  开始", font=self.font_button,
            bg=self.ACCENT_COLOR, fg="white", activebackground=self.ACCENT_HOVER,
            activeforeground="white", relief="flat", cursor="hand2",
            command=self.toggle_clicking, height=2
        )
        self.start_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.start_button.bind("<Enter>", lambda e: self.start_button.configure(
            bg=self.ACCENT_HOVER if not self._running else self.STOP_HOVER))
        self.start_button.bind("<Leave>", lambda e: self.start_button.configure(
            bg=self.ACCENT_COLOR if not self._running else self.STOP_COLOR))

    def reset_counter(self):
        self.clicker.reset_counter()
        self.click_count_var.set("0")

    def toggle_recording(self):
        if self.macro_manager.is_recording:
            self.macro_manager.stop_recording()
        else:
            if self.macro_manager.is_playing:
                self.macro_manager.stop_playback()
            self.macro_manager.start_recording()

    def _on_macro_record_start(self):
        self.root.after(0, self._update_macro_recording)

    def _on_macro_record_stop(self):
        self.root.after(0, self._update_macro_recorded)

    def _update_macro_recording(self):
        self.record_button.configure(text="■ 停止录制", bg=self.STOP_COLOR)
        self.macro_status_var.set("录制中...")
        self.status_label.configure(text="● 录制中", style="Recording.TLabel")

    def _update_macro_recorded(self):
        count = self.macro_manager.get_action_count()
        duration = self.macro_manager.get_duration()
        self.record_button.configure(text="● 录制", bg=self.RECORD_COLOR)
        self.macro_status_var.set(f"已录制 {count} 个操作 ({duration:.1f}秒)")
        self._update_status_stopped()

    def toggle_playback(self):
        if self.macro_manager.is_playing:
            self.macro_manager.stop_playback()
        else:
            if self.macro_manager.is_recording:
                self.macro_manager.stop_recording()
            self.macro_manager.start_playback()

    def _on_macro_play_start(self):
        self.root.after(0, self._update_macro_playing)

    def _on_macro_play_stop(self):
        self.root.after(0, self._update_macro_stopped)

    def _update_macro_playing(self):
        self.play_button.configure(text="■ 停止回放", bg=self.STOP_COLOR)
        self.macro_status_var.set("回放中...")
        self.status_label.configure(text="● 回放中", style="Running.TLabel")

    def _update_macro_stopped(self):
        self.play_button.configure(text="▶ 回放", bg=self.ACCENT_COLOR)
        count = self.macro_manager.get_action_count()
        self.macro_status_var.set(f"回放完成 ({count} 个操作)")
        self._update_status_stopped()

    def save_macro(self):
        if not self.macro_manager.recorded_actions:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("宏文件", "*.json"), ("所有文件", "*.*")],
            title="保存宏"
        )
        if filepath:
            self.macro_manager.save_macro(filepath)
            self.macro_file_var.set(filepath)

    def load_macro(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("宏文件", "*.json"), ("所有文件", "*.*")],
            title="加载宏"
        )
        if filepath:
            self.macro_manager.load_macro(filepath)
            self.macro_file_var.set(filepath)
            count = self.macro_manager.get_action_count()
            duration = self.macro_manager.get_duration()
            self.macro_status_var.set(f"已加载 {count} 个操作 ({duration:.1f}秒)")

    def _on_close_to_tray_changed(self):
        self.save_config()

    def save_preset(self):
        name = self.preset_name_var.get().strip()
        if not name:
            return
        config = {
            "hotkey": self.hotkey_var.get(),
            "mode": self.mode_var.get(),
            "interval": self.interval_var.get(),
            "target": self.target_var.get(),
            "key": self.key_var.get(),
            "max_clicks": self.max_clicks_var.get(),
            "max_seconds": self.max_seconds_var.get(),
            "random_enabled": self.random_enabled_var.get(),
            "random_range": self.random_range_var.get()
        }
        self.preset_manager.save_preset(name, config)
        self.preset_combo["values"] = self.preset_manager.get_preset_names()
        self.selected_preset_var.set(name)
        self.preset_name_var.set("")

    def load_preset(self):
        name = self.selected_preset_var.get()
        if not name:
            return
        config = self.preset_manager.get_preset(name)
        if config:
            self.hotkey_var.set(config.get("hotkey", "F6"))
            self.mode_var.set(config.get("mode", "toggle"))
            self.interval_var.set(config.get("interval", 100))
            self.target_var.set(config.get("target", "keyboard"))
            self.key_var.set(config.get("key", "a"))
            self.max_clicks_var.set(config.get("max_clicks", 0))
            self.max_seconds_var.set(config.get("max_seconds", 0))
            self.random_enabled_var.set(config.get("random_enabled", False))
            self.random_range_var.set(config.get("random_range", 50))
            self.save_config()

    def delete_preset(self):
        name = self.selected_preset_var.get()
        if not name:
            return
        if self.preset_manager.delete_preset(name):
            self.preset_combo["values"] = self.preset_manager.get_preset_names()
            self.selected_preset_var.set("")

    def load_config(self):
        config = self.config_manager.load_config()
        self.hotkey_var.set(config.get("hotkey", "F6"))
        self.mode_var.set(config.get("mode", "toggle"))
        self.interval_var.set(config.get("interval", 100))
        self.target_var.set(config.get("target", "keyboard"))
        self.key_var.set(config.get("key", "a"))
        self.close_to_tray_var.set(config.get("close_to_tray", True))
        self.max_clicks_var.set(config.get("max_clicks", 0))
        self.max_seconds_var.set(config.get("max_seconds", 0))
        self.random_enabled_var.set(config.get("random_enabled", False))
        self.random_range_var.set(config.get("random_range", 50))

    def save_config(self):
        config = {
            "hotkey": self.hotkey_var.get(),
            "mode": self.mode_var.get(),
            "interval": self.interval_var.get(),
            "target": self.target_var.get(),
            "key": self.key_var.get(),
            "close_to_tray": self.close_to_tray_var.get(),
            "max_clicks": self.max_clicks_var.get(),
            "max_seconds": self.max_seconds_var.get(),
            "random_enabled": self.random_enabled_var.get(),
            "random_range": self.random_range_var.get()
        }
        self.config_manager.save_config(config)

    def _start_hotkey_listener(self):
        self.hotkey_listener.set_hotkey(self.hotkey_var.get())
        self.hotkey_listener.set_mode(self.mode_var.get())
        self.hotkey_listener.start_listening(self._on_hotkey_triggered)

    def _on_hotkey_triggered(self):
        self.root.after(0, self.toggle_clicking)

    def set_hotkey(self):
        self.status_label.configure(text="● 请按下新热键...", style="Status.TLabel")
        self.hotkey_entry.configure(foreground="#999999")
        self.root.bind("<KeyPress>", self.on_hotkey_pressed)

    def on_hotkey_pressed(self, event):
        new_hotkey = event.keysym
        self.hotkey_var.set(new_hotkey)
        self.root.unbind("<KeyPress>")
        self.hotkey_entry.configure(foreground=self.TEXT_COLOR)
        self._update_status_stopped()
        self.save_config()
        self.hotkey_listener.set_hotkey(new_hotkey)

    def set_key(self):
        self.status_label.configure(text="● 请按下新按键...", style="Status.TLabel")
        self.key_entry.configure(foreground="#999999")
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
        self.key_entry.configure(foreground=self.TEXT_COLOR)
        self._update_status_stopped()
        self.save_config()

    def on_mouse_button_pressed(self, event):
        button_map = {1: "left", 2: "middle", 3: "right"}
        button_name = button_map.get(event.num, "left")
        self.key_var.set(button_name)
        self.root.unbind("<ButtonPress-1>")
        self.root.unbind("<ButtonPress-2>")
        self.root.unbind("<ButtonPress-3>")
        self.key_entry.configure(foreground=self.TEXT_COLOR)
        self._update_status_stopped()
        self.save_config()

    def _update_status_stopped(self):
        self.status_label.configure(text="● 已停止", style="Status.TLabel")

    def _update_status_running(self):
        self.status_label.configure(text="● 运行中", style="Running.TLabel")

    def toggle_clicking(self):
        if self._running:
            self.clicker.stop_clicking()
            self._running = False
            self._stop_timer()
            self.start_button.configure(text="▶  开始", bg=self.ACCENT_COLOR)
            self.start_button.unbind("<Enter>")
            self.start_button.unbind("<Leave>")
            self.start_button.bind("<Enter>", lambda e: self.start_button.configure(bg=self.ACCENT_HOVER))
            self.start_button.bind("<Leave>", lambda e: self.start_button.configure(bg=self.ACCENT_COLOR))
            self._update_status_stopped()
        else:
            self.save_config()
            self.hotkey_listener.set_hotkey(self.hotkey_var.get())
            self.hotkey_listener.set_mode(self.mode_var.get())
            self.clicker.set_target(self.target_var.get())
            self.clicker.set_key(self.key_var.get())
            self.clicker.set_interval(self.interval_var.get())
            self.clicker.set_max_clicks(self.max_clicks_var.get())
            self.clicker.set_max_seconds(self.max_seconds_var.get())
            self.clicker.set_random_interval(self.random_enabled_var.get(), self.random_range_var.get())
            self.clicker.start_clicking()
            self._running = True
            self.start_button.configure(text="■  停止", bg=self.STOP_COLOR)
            self.start_button.unbind("<Enter>")
            self.start_button.unbind("<Leave>")
            self.start_button.bind("<Enter>", lambda e: self.start_button.configure(bg=self.STOP_HOVER))
            self.start_button.bind("<Leave>", lambda e: self.start_button.configure(bg=self.STOP_COLOR))
            self._update_status_running()
            self._start_timer()

    def _create_tray_icon(self):
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        color = self.RUNNING_COLOR if self._running else "#4a90d9"
        draw.ellipse([8, 8, 56, 56], fill=color, outline="white", width=3)
        draw.text((22, 18), "⚡", fill="white")
        return image

    def _show_window(self, icon=None, item=None):
        if icon:
            icon.stop()
            self._tray_icon = None
        self.root.after(0, self._do_show_window)

    def _do_show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _quit_program(self, icon=None, item=None):
        if icon:
            icon.stop()
            self._tray_icon = None
        self.root.after(0, self._do_quit)

    def _do_quit(self):
        self.hotkey_listener.stop_listening()
        if self._running:
            self.clicker.stop_clicking()
        if self.macro_manager.is_recording:
            self.macro_manager.stop_recording()
        if self.macro_manager.is_playing:
            self.macro_manager.stop_playback()
        self._stop_timer()
        self.root.destroy()

    def _minimize_to_tray(self):
        self.save_config()
        menu = pystray.Menu(
            pystray.MenuItem("显示窗口", self._show_window, default=True),
            pystray.MenuItem("退出", self._quit_program)
        )
        self._tray_icon = pystray.Icon(
            "连点器",
            self._create_tray_icon(),
            "连点器 - 后台运行中",
            menu
        )
        self.root.withdraw()
        tray_thread = threading.Thread(target=self._tray_icon.run, daemon=True)
        tray_thread.start()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.close_to_tray_var.get():
            self._minimize_to_tray()
        else:
            self._do_quit()
