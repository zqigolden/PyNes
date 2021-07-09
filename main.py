#!/usr/bin/env python3
import sys 
import typer
from pynes.ppu import PPU
from pynes.cpu import CPU
from pynes.bus import Bus
from pynes.cartridge import Cartridge
from loguru import logger
import time

logger.remove()
logger.add(sys.stderr, level="INFO")

@logger.catch
def main(debug:int=typer.Option(-1, '-d', '--debug')):

    bus = Bus()
    bus.connect(CPU())
    bus.connect(PPU())
    # bus.connect_cartridge(Cartridge('roms/Tetris (USA) (Tengen) (Unl).nes'))
    # bus.connect_cartridge(Cartridge('roms/Pac-Man (USA) (Namco).nes'))
    bus.connect_cartridge(Cartridge('roms/full_palette.nes'))
    # bus.connect_cartridge(Cartridge('roms/helloworld.nes'))
    # bus.connect_cartridge(Cartridge('roms/starter.nes'))
    bus.reset()
    DEBUG = False

    ts = time.time()
    while True:
        c = bus.nSystemClockCounter
        cpu_cycle = bus.cpu.clock_count
        debug_ready = not bus.dma_transfer and bus.cpu.cycles == 0
        if c % 100000 == 0:
            logger.info(f'cycles: {c}, cpu_cycle: {cpu_cycle}')
        if c == 1000000:
            logger.info(f'time spend: {time.time() - ts}')
            break
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