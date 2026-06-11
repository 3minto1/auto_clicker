# main.py
import sys
import ctypes

def hide_console_window():
    """Hide the console window on Windows."""
    if sys.platform == 'win32':
        try:
            # Get the console window handle
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            if console_window:
                # SW_HIDE = 0
                ctypes.windll.user32.ShowWindow(console_window, 0)
        except Exception:
            # If we can't hide the console, just continue
            pass

def main():
    hide_console_window()
    app = AutoClickerGUI()
    app.run()

if __name__ == "__main__":
    main()
