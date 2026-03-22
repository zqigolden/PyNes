# PyNes

[中文说明](README-CN.md)

## Introduction

PyNes is a project focused on building a fully functional NES (Nintendo Entertainment System) simulator using Python and Pygame. It serves as an educational tool to understand the low-level hardware interactions and cycle-accurate emulation of classic retro gaming consoles.

## Requirements

Ensure you have Python 3 installed. You can install all necessary dependencies using `pip`:

```bash
pip install -r requirements.txt
```

The core dependencies are:
- `pygame` (Rendering and input processing)
- `loguru` (Logging and debugging)
- `typer` (CLI support)
- `easydict` & `bitarray` (Data structures and bit manipulation)

## Usage

To start the emulator, simply run the main script from the root directory:

```bash
python main.py
```

By default, the emulator loads the Pac-Man sample ROM located in the `roms/` directory.

### Controls

The standard PC keyboard is mapped to the NES controller as follows:

| NES Button | PC Key |
|------------|--------|
| A          | Z      |
| B          | X      |
| Select     | A      |
| Start      | S      |
| D-Pad Up   | Up Arrow |
| D-Pad Down | Down Arrow |
| D-Pad Left | Left Arrow |
| D-Pad Right| Right Arrow |

## Structure

The emulator is separated into distinct modular hardware components:

- **Bus (`bus.py`)**: The central communication backbone. It connects the CPU, PPU, RAM, and cartridges, routing read/write operations to the correct device mapped in memory.
- **CPU (`cpu.py`)**: An emulation of the Ricoh 2A03 (MOS 6502 based) processor. It handles fetching, decoding, and executing instructions and managing internal registers.
- **PPU (`ppu.py`)**: The Picture Processing Unit (Ricoh 2C02). It is responsible for rendering graphics, backgrounds (NameTables), and sprites (OAM) to the screen.
- **Cartridge & Mapper (`cartridge.py`, `mapper.py`)**: Handles loading `.nes` ROM files and manages memory bank switching (Mappers) to map PRG and CHR ROM data into the CPU and PPU address spaces.
- **Engine (`engine.py`)**: The Pygame frontend responsible for painting pixels to the display window and polling hardware keyboard events.
