# AutoClicker - 高频连点器

一个基于 Python 的高频连点器，支持键盘和鼠标模拟，可配置热键和点击间隔。

## 功能特点

- **键盘模拟**：模拟任意键盘按键，包括修饰键（Shift、Ctrl、Alt）
- **鼠标模拟**：模拟鼠标左键、右键、中键点击
- **全局热键**：支持全局热键启动/停止，不受窗口焦点影响
- **两种启动模式**：
  - 点按模式：按一次热键开始，再按一次停止
  - 长按模式：按住热键时运行，松开时停止
- **可配置点击间隔**：1-1000毫秒
- **热键自定义**：通过GUI界面设置任意按键作为热键
- **现代界面**：卡片式布局，支持窗口缩放和字体等比缩放
- **配置持久化**：设置自动保存，下次启动自动加载

## 安装

```bash
# 克隆仓库
git clone https://github.com/3minto1/auto-clicker.git
cd auto-clicker

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

```bash
# 启动程序
python main.py

# 无黑窗口启动（Windows）
pythonw main.py
# 或双击 启动连点器.vbs
```

## 操作说明

1. **设置启动热键**：点击"设置"按钮，按下你想要的热键（默认F6）
2. **选择启动模式**：点按切换 或 长按生效
3. **选择模拟目标**：键盘按键 或 鼠标按钮
4. **设置模拟按键**：点击"设置"按钮，按下要模拟的键/按钮
5. **设置点击间隔**：输入1-1000毫秒的数值
6. **开始/停止**：点击主按钮或按热键

## 项目结构

```
auto-clicker/
├── main.py              # 主程序入口
├── gui.py               # GUI界面模块
├── hotkey_listener.py   # 全局热键监听模块
├── clicker.py           # 模拟点击模块
├── config_manager.py    # 配置管理模块
├── requirements.txt     # 依赖列表
├── 启动连点器.vbs        # 无窗口启动脚本
└── tests/               # 测试目录
```

## 测试

```bash
pytest tests/ -v
```

## 技术栈

- Python 3.10+
- pynput - 全局键盘/鼠标监听与模拟
- tkinter - GUI界面

## 许可证

MIT License
