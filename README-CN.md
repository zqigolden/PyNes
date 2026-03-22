# PyNes

[English Documentation](README.md)

## 简介 (Introduction)

PyNes 是一个旨在利用 Python 和 Pygame 构建一个功能完善的 NES（Nintendo Entertainment System）模拟器项目。它是一个非常有用的教育工具，有助于理解复古游戏机的底层硬件交互和基于周期的精准模拟技术。

## 依赖要求 (Requirements)

请确保你的系统上安装了 Python 3。您可以使用 `pip` 命令安装所有必需的依赖：

```bash
pip install -r requirements.txt
```

项目的核心依赖库：
- `pygame` (用于屏幕渲染和输入捕获)
- `loguru` (用于日志记录和调试)
- `typer` (支持命令行参数)
- `easydict` 和 `bitarray` (数据结构和位操作)

## 使用方法 (Usage)

在项目的根目录下执行以下脚本即可启动模拟器：

```bash
python main.py
```

默认情况下，模拟器会加载 `roms/` 文件夹下的《吃豆人》(Pac-Man) 示例游戏。

### 操作说明 (Controls)

标准的 PC 键盘与 NES 手柄的映射关系如下：

| NES 手柄按键 | PC 键盘按键 |
|--------------|-------------|
| A            | Z           |
| B            | X           |
| Select       | A           |
| Start        | S           |
| 方向键 上    | 上箭头      |
| 方向键 下    | 下箭头      |
| 方向键 左    | 左箭头      |
| 方向键 右    | 右箭头      |

## 项目架构 (Structure)

模拟器分为独立的模块化硬件组件：

- **总线 Bus (`bus.py`)**：核心的通信中枢。负责连接 CPU、PPU、内存 RAM 和卡带，并将读写操作路由到映射到正确内存地址的设备。
- **中央处理器 CPU (`cpu.py`)**：模拟 Ricoh 2A03 (基于 MOS 6502) 处理器。主要负责取指、解码、执行指令，以及管理内部寄存器。
- **图形处理器 PPU (`ppu.py`)**：图像处理单元 (Ricoh 2C02)。主要负责将图形、背景（NameTables）和精灵（OAM）渲染到屏幕上。
- **卡带与内存映射 Cartridge & Mapper (`cartridge.py`, `mapper.py`)**：负责加载 `.nes` ROM 文件，并处理内存 Bank 的切换（Mapper），将 PRG 和 CHR ROM 数据映射到 CPU 和 PPU 的寻址空间中。
- **引擎 Engine (`engine.py`)**：使用 Pygame 封装的前端界面。负责将像素绘制到显示窗口并持续轮询硬件键盘事件。
