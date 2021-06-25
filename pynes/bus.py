from pynes.bits import mtx
from pynes.bits import assert_u16, assert_u8
from typing import Any, Dict, Tuple

from pynes.bits import t8, t16, u16, u8
from pynes.cartridge import Cartridge
from pynes.cpu import CPU
from pynes.ppu import PPU
from pynes.device import Device
import loguru


class Bus(Device):
    def __init__(self, address_count: int = 16, data_count: int = 8, name: str = '') -> None:
        super().__init__(name=name)
        self.address_count = address_count
        self.data_count = data_count
        self.read_only = False
        self.cartridge = None
        self.cpu = None
        self.ppu = None
        self.nSystemClockCounter = 0
        self.cpuRam = mtx(0, 2048)
        self.controller = [0, 0]
        self.controller_state = [0, 0]

    def connect(self, device: Device, name: str = None) -> None:
        if isinstance(device, CPU):
            device.connect_bus(self)
            self.cpu = device
        if isinstance(device, PPU):
            self.ppu = device
            if self.cartridge:
                self.ppu.cartridge = self.cartridge

    def connect_cartridge(self, cart: Cartridge):
        self.cartridge = cart
        if self.ppu:
            self.ppu.cartridge = cart

    def read(self, addr: t16) -> t8:
        assert_u16(addr)
        addr = u16(addr)
        data = self.cartridge.read(addr)
        if data is not False:
            pass
        elif 0x0000 <= addr <= 0x1FFF:
            data = self.cpuRam[addr & 0x07FF]
        elif 0x2000 <= addr <= 0x3FFF:
            data = self.ppu.read(addr & 0x0007)
        elif 0x4016 <= addr <= 0x4017:
            data = int((self.controller_state[addr & 0x0001] & 0x80) > 0)
            self.controller_state[addr & 0x0001] <<= 1
        #loguru.logger.debug('0x{:02x} read from cart at 0x{:04x}', data, addr)
        #loguru.logger.debug('0x{:02x} read from {} at 0x{:04x}', data, device[1].name, addr)
        assert_u8(data)
        return data

    def write(self, addr: t16, data: t8) -> None:
        assert_u16(addr)
        assert_u8(data)
        if self.cartridge.write(addr, data):
            #loguru.logger.debug('0x{:02x} write to cart at 0x{:04x}', data, addr)
            return
            #loguru.logger.debug('0x{:02x} write to {} at 0x{:04x}', data, device[1].name, addr)
        elif 0x0000 <= addr <= 0x1FFF:
            self.cpuRam[addr & 0x07FF] = data
        elif 0x2000 <= addr <= 0x3FFF:
            self.ppu.write(addr & 0x0007, data)
        elif 0x4016 <= addr <= 0x4017:
            self.controller_state[addr & 0x0001] = self.controller[addr & 0x0001]

    def reset(self) -> None:
        if self.cartridge:
            self.cartridge.reset()
        if self.cpu:
            self.cpu.reset()
        if self.ppu:
            self.ppu.reset()
        self.nSystemClockCounter = 0


    def clock(self) -> None:
        self.ppu.clock()
        if self.nSystemClockCounter % 3 == 0:
            self.cpu.clock()
        if self.ppu.nmi:
            self.ppu.nmi = False
            self.cpu.nmi()
        self.nSystemClockCounter += 1


if __name__ == '__main__':
    print(Bus())
    b1 = Bus(name='bus1')
    b1.connect(Bus(name='bus2'), [0x00, 0xff])
    b1.connect(Bus(name='bus3'), [0x100, 0x1ff])
    #b1.connect(Bus(name='bus4'), [0x1ff, 0x2ff])
    print(b1)
