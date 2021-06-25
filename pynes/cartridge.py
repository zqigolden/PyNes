from pathlib import Path
from struct import unpack_from
from collections import namedtuple

from loguru import logger
from pynes.mapper import Mapper, Mapper003, Mapper000
from pynes.bits import uint8, uint16, u8, u16, t16, t8, assert_u16
from pynes.device import Device

Header = namedtuple('Header',
                    'name prg_rom_chunks chr_rom_chunks mapper1 mapper2 prg_ram_size tv_system1 tv_system2')

HORIZONTAL = 0
VERTICAL = 1
ONESCREEN_LO = 2
ONESCREEN_HI = 3

class Cartridge(Device):
    def __init__(self, file_name: str) -> None:
        self.file_name = Path(file_name)
        super().__init__(name=self.file_name.stem)
        data = self.file_name.read_bytes()
        self.nMapperID = u8()
        self.nPRGBanks = u8()
        self.nCHRBanks = u8()

        self.vPRGMemory: int = None
        self.vCHRMemory: int = None

        self.mapper: Mapper = None
        self.bImageValid = False

        header = Header(*unpack_from('4s7B', data))
        offset = 16
        if header.mapper1 & 0x04:
            offset += 512
        self.nMapperID = ((header.mapper2 >> 4) << 4) | (header.mapper1 >> 4)
        self.mirror = VERTICAL if header.mapper1 & 0x01 else HORIZONTAL

        logger.info(f'using mapper {self.nMapperID}')

        nFileType = 1
        # if header.mapper2 & 0x0C == 0x08: 
        #     nFileType = 2

        if nFileType == 0:
            pass

        if nFileType == 1:
            self.nPRGBanks = header.prg_rom_chunks
            self.vPRGMemory = list(unpack_from(f'{self.nPRGBanks * 16 * 1024}B', data, offset=offset))
            offset += self.nPRGBanks * 16 * 1024
            if self.nCHRBanks == 0:
                CBanks = 1
            else:
                CBanks = self.nCHRBanks
            self.vCHRMemory = list(unpack_from(f'{CBanks * 8 * 1024}B', data, offset=offset))
            offset += CBanks * 8 * 1024

        # if (nFileType == 2)
        # {
        #     nPRGBanks = ((header.prg_ram_size & 0x07) << 8) | header.prg_rom_chunks;
        #     vPRGMemory.resize(nPRGBanks * 16384);
        #     ifs.read((char*)vPRGMemory.data(), vPRGMemory.size());

        #     nCHRBanks = ((header.prg_ram_size & 0x38) << 8) | header.chr_rom_chunks;
        #     vCHRMemory.resize(nCHRBanks * 8192);
        #     ifs.read((char*)vCHRMemory.data(), vCHRMemory.size());
        # }

        # // Load appropriate mapper
        # switch (nMapperID)
        # {
        # case   0: pMapper = std::make_shared<Mapper_000>(nPRGBanks, nCHRBanks); break;
        # case   1: pMapper = std::make_shared<Mapper_001>(nPRGBanks, nCHRBanks); break;
        # case   2: pMapper = std::make_shared<Mapper_002>(nPRGBanks, nCHRBanks); break;
        # case   3: pMapper = std::make_shared<Mapper_003>(nPRGBanks, nCHRBanks); break;
        # case   4: pMapper = std::make_shared<Mapper_004>(nPRGBanks, nCHRBanks); break;
        # case  66: pMapper = std::make_shared<Mapper_066>(nPRGBanks, nCHRBanks); break;

        # }

        mappers = {
            0: Mapper000,
            3: Mapper003,
        }
        self.mapper = mappers.get(self.nMapperID, Mapper)(self.nPRGBanks, self.nCHRBanks)
        self.bImageValid = True


    def image_valid(self) -> bool:
        return self.bImageValid

    def read(self, addr: t16) -> t8:
        assert_u16(addr)
        mapped_addr, result = self.mapper.cpuMapRead(addr)
        if result:
            return self.vPRGMemory[mapped_addr]
        else:
            return False

    def write(self, addr: t16, data: t8) -> None:
        assert_u16(addr)
        mapped_addr, result = self.mapper.cpuMapWrite(addr, data)
        if result:
            self.vPRGMemory[mapped_addr] = data
            return True
        else:
            return False
    
    def ppuRead(self, addr: t16) -> t8:
        assert_u16(addr)
        mapped_addr, result = self.mapper.ppuMapRead(addr)
        if result:
            return self.vCHRMemory[mapped_addr]
        else:
            return False

    def ppuWrite(self, addr: t16, data: t8) -> None:
        assert_u16(addr)
        mapped_addr, result = self.mapper.ppuMapWrite(addr, data)
        if result:
            self.vCHRMemory[mapped_addr] = data
            return True
        else:
            return False
    
    def reset(self) -> None:
        if self.mapper:
            self.mapper.reset()

if __name__ == '__main__':
    print(Cartridge('roms/Tetris (USA) (Tengen) (Unl).nes'))
