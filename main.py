#!/usr/bin/env python3
import sys 
import typer
from pynes.ppu import PPU
from pynes.cpu import CPU
from pynes.bus import Bus
from pynes.cartridge import Cartridge
from loguru import logger
import time

@logger.catch
def main(DEBUG:bool=False):
    if not DEBUG:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    bus = Bus()
    bus.connect(CPU(debug=DEBUG))
    bus.connect(PPU())
    #bus.connect_cartridge(Cartridge('roms/Tetris (USA) (Tengen) (Unl).nes'))
    bus.connect_cartridge(Cartridge('roms/Pac-Man (USA) (Namco).nes'))
    #bus.connect_cartridge(Cartridge('roms/full_palette.nes'))
    bus.reset()

    logger.debug(bus)
    c = 0
    ts = time.time()
    while True:
        if c % 100000 == 0:
            logger.info(f'cycles: {c}')
            print(bus.ppu.tblPalette)
        if c == 1000000:
            logger.info(f'time spend: {time.time() - ts}')
            exit()
        bus.clock()
        if DEBUG and c % 30 == 0:
            #input('paused')
            pass
        c += 1
typer.run(main)