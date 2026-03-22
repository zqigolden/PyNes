#!/usr/bin/env python3
import sys 
import typer
from pynes.ppu import PPU
from pynes.cpu import CPU
from pynes.bus import Bus
from pynes.cartridge import Cartridge
from loguru import logger
import time
import pygame

logger.remove()
logger.add(sys.stderr, level="INFO")

@logger.catch
def main(debug:int=typer.Option(-1, '-d', '--debug')):
    """
    Main entrypoint of the NES Simulator. It initializes the core system components (Bus, CPU, PPU),
    connects the game cartridge, and starts the infinite loop to run system clock cycles until
    the user quits the Pygame window.
    """

    bus = Bus()
    bus.connect(CPU())
    bus.connect(PPU())
    # bus.connect_cartridge(Cartridge('roms/Tetris (USA) (Tengen) (Unl).nes'))
    bus.connect_cartridge(Cartridge('roms/Pac-Man (USA) (Namco).nes'))
    # bus.connect_cartridge(Cartridge('roms/full_palette.nes'))
    # bus.connect_cartridge(Cartridge('roms/helloworld.nes'))
    # bus.connect_cartridge(Cartridge('roms/starter.nes'))
    bus.reset()
    DEBUG = False

    ts = time.time()

    while not bus.ppu.engine.finished:
        c = bus.nSystemClockCounter
        cpu_cycle = bus.cpu.clock_count
        debug_ready = not bus.dma_transfer and bus.cpu.cycles == 0

        # Poll inputs once per frame (PPU updates on scanline 261)
        if bus.ppu.frame_complete:
            bus.ppu.frame_complete = False
            keys = bus.ppu.engine.get_keys()
            if keys:
                # NES controller layout: A, B, Select, Start, Up, Down, Left, Right
                controller = 0
                controller |= (1 << 7) if keys[pygame.K_z] else 0      # A
                controller |= (1 << 6) if keys[pygame.K_x] else 0      # B
                controller |= (1 << 5) if keys[pygame.K_a] else 0      # Select
                controller |= (1 << 4) if keys[pygame.K_s] else 0      # Start
                controller |= (1 << 3) if keys[pygame.K_UP] else 0     # Up
                controller |= (1 << 2) if keys[pygame.K_DOWN] else 0   # Down
                controller |= (1 << 1) if keys[pygame.K_LEFT] else 0   # Left
                controller |= (1 << 0) if keys[pygame.K_RIGHT] else 0  # Right
                bus.controller[0] = controller

        if c % 100000 == 0:
            logger.info(f'cycles: {c}, cpu_cycle: {cpu_cycle}')
        bus.clock()
        #[86694, 655061] target 655061
        if cpu_cycle == debug and not DEBUG:
            DEBUG = True
            bus.cpu.debug = True
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")
        if c % 3 == 0:
            if DEBUG and debug_ready:
                input('pause')
        
typer.run(main)