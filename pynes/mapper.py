from pynes.bits import assert_u16
from typing import Tuple
from pynes.bits import uint8, uint16, u8, u16, t16, t8
from pynes.device import Device


class Mapper(Device):
    def __init__(self, prgBanks, chrBanks, name: str = None) -> None:
        super().__init__(name)
        self.nPRGBanks = prgBanks
        self.nCHRBanks = chrBanks

    def cpuMapRead(self, addr:t16) -> Tuple[t16, bool]:
        raise NotImplementedError
    def cpuMapWrite(self, addr:t16, value:t8) -> Tuple[t16, bool]:
        raise NotImplementedError
    def ppuMapRead(self, addr:t16) -> Tuple[t16, bool]:
        raise NotImplementedError
    def ppuMapWrite(self, addr:t16, value:t8) -> Tuple[t16, bool]:
        raise NotImplementedError
    def scanline(self) -> None:
        return

class Mapper000(Mapper):
    def __init__(self, prgBanks, chrBanks, name: str = None) -> None:
        super().__init__(prgBanks, chrBanks, name=name)

    def cpuMapRead(self, addr:t16) -> Tuple[t16, bool]:
        assert_u16(addr)
        if 0x8000 <= addr <= 0xFFFF:
            mapped_addr = addr & (0x7FFF if self.nPRGBanks > 1 else 0x3FFF)
            return mapped_addr, True
        else:
            return u16(), False

    def cpuMapWrite(self, addr: t16, value: t8) -> Tuple[t16, bool]:
        assert_u16(addr)
        if 0x8000 <= addr <= 0xFFFF:
            mapped_addr = addr & (0x7FFF if self.nPRGBanks > 1 else 0x3FFF)
            return mapped_addr, True
        else:
            return u16(), False

    def ppuMapRead(self, addr: t16) -> Tuple[t16, bool]:
        assert_u16(addr)
        if 0x0000 <= addr <= 0x1FFF:
            return addr, True
        else:
            return u16(), False

    def ppuMapWrite(self, addr: t16, value: t8) -> Tuple[t16, bool]:
        assert_u16(addr)
        if 0x0000 <= addr <= 0x1FFF:
            if self.nCHRBanks == 0:
                return addr, True
        return u16(), False

    def reset(self) -> None:
        pass

class Mapper003(Mapper):
    def __init__(self, prgBanks, chrBanks, name: str = None) -> None:
        super().__init__(prgBanks, chrBanks, name=name)
        self.nCHRBankSelect = u8()

    def cpuMapRead(self, addr:t16) -> Tuple[t16, bool]:
        assert_u16(addr)
        if 0x8000 <= addr <= 0xFFFF:
            if self.nPRGBanks == 1:
                mapped_addr = addr & 0x3FFF
            if self.nPRGBanks == 2:
                mapped_addr = addr & 0x7FFF
            return mapped_addr, True
        else:
            return u16(), False

    def cpuMapWrite(self, addr: t16, value: t8) -> Tuple[t16, bool]:
        assert_u16(addr)
        if 0x8000 <= addr <= 0xFFFF:
            self.nCHRBankSelect = value & 0x03
        return addr, False

    def ppuMapRead(self, addr: t16) -> Tuple[t16, bool]:
        assert_u16(addr)
        if addr < 0x2000:
            return self.nCHRBankSelect * 0x2000 + addr, True
        else:
            return None, False

    def ppuMapWrite(self, addr: t16, value: t8) -> Tuple[t16, bool]:
        assert_u16(addr)
        return u16(), False

    def reset(self) -> None:
        self.nCHRBankSelect = u8()
