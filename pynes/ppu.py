from loguru import logger
from pynes.bits import assert_u16
from easydict import EasyDict
from pynes.bits import uint8, uint16, u8, u16, t8, t16, mtx
from pynes.device import Device
from pynes.cartridge import Cartridge, VERTICAL, HORIZONTAL
from pynes.engine import Engine

palScreen = [None] * 0x40
palScreen[0x00] = (84, 84, 84)
palScreen[0x01] = (0, 30, 116)
palScreen[0x02] = (8, 16, 144)
palScreen[0x03] = (48, 0, 136)
palScreen[0x04] = (68, 0, 100)
palScreen[0x05] = (92, 0, 48)
palScreen[0x06] = (84, 4, 0)
palScreen[0x07] = (60, 24, 0)
palScreen[0x08] = (32, 42, 0)
palScreen[0x09] = (8, 58, 0)
palScreen[0x0A] = (0, 64, 0)
palScreen[0x0B] = (0, 60, 0)
palScreen[0x0C] = (0, 50, 60)
palScreen[0x0D] = (0, 0, 0)
palScreen[0x0E] = (0, 0, 0)
palScreen[0x0F] = (0, 0, 0)

palScreen[0x10] = (152, 150, 152)
palScreen[0x11] = (8, 76, 196)
palScreen[0x12] = (48, 50, 236)
palScreen[0x13] = (92, 30, 228)
palScreen[0x14] = (136, 20, 176)
palScreen[0x15] = (160, 20, 100)
palScreen[0x16] = (152, 34, 32)
palScreen[0x17] = (120, 60, 0)
palScreen[0x18] = (84, 90, 0)
palScreen[0x19] = (40, 114, 0)
palScreen[0x1A] = (8, 124, 0)
palScreen[0x1B] = (0, 118, 40)
palScreen[0x1C] = (0, 102, 120)
palScreen[0x1D] = (0, 0, 0)
palScreen[0x1E] = (0, 0, 0)
palScreen[0x1F] = (0, 0, 0)

palScreen[0x20] = (236, 238, 236)
palScreen[0x21] = (76, 154, 236)
palScreen[0x22] = (120, 124, 236)
palScreen[0x23] = (176, 98, 236)
palScreen[0x24] = (228, 84, 236)
palScreen[0x25] = (236, 88, 180)
palScreen[0x26] = (236, 106, 100)
palScreen[0x27] = (212, 136, 32)
palScreen[0x28] = (160, 170, 0)
palScreen[0x29] = (116, 196, 0)
palScreen[0x2A] = (76, 208, 32)
palScreen[0x2B] = (56, 204, 108)
palScreen[0x2C] = (56, 180, 204)
palScreen[0x2D] = (60, 60, 60)
palScreen[0x2E] = (0, 0, 0)
palScreen[0x2F] = (0, 0, 0)

palScreen[0x30] = (236, 238, 236)
palScreen[0x31] = (168, 204, 236)
palScreen[0x32] = (188, 188, 236)
palScreen[0x33] = (212, 178, 236)
palScreen[0x34] = (236, 174, 236)
palScreen[0x35] = (236, 174, 212)
palScreen[0x36] = (236, 180, 176)
palScreen[0x37] = (228, 196, 144)
palScreen[0x38] = (204, 210, 120)
palScreen[0x39] = (180, 222, 120)
palScreen[0x3A] = (168, 226, 144)
palScreen[0x3B] = (152, 226, 180)
palScreen[0x3C] = (160, 214, 228)
palScreen[0x3D] = (160, 162, 160)
palScreen[0x3E] = (0, 0, 0)
palScreen[0x3F] = (0, 0, 0)

STATUS_FLAG = EasyDict(
    unused1 = 1 << 0,
    unused2 = 1 << 1,
    unused3 = 1 << 2,
    unused4 = 1 << 3,
    unused5 = 1 << 4,
    sprite_overflow = 1 << 5,
    sprite_zero_hit = 1 << 6,
    vertical_blank = 1 << 7
    )

MASK_FLAG = EasyDict(
    grayscale = 1 << 0,
    render_background_left = 1 << 1,
    render_sprites_left = 1 << 2,
    render_background = 1 << 3,
    render_sprites = 1 << 4,
    enhance_red = 1 << 5,
    enhance_green = 1 << 6,
    enhance_blue = 1 << 7,
)

CONTROL_FLAG = EasyDict(
    nametable_x = 1 << 0,
    nametable_Y = 1 << 1,
    increment_mode = 1 << 2,
    pattern_sprite = 1 << 3,
    pattern_background = 1 << 4,
    sprite_size = 1 << 5,
    slave_mode = 1 << 6,
    enable_nmi = 1 << 7,
)

LOOPY_FLAG = EasyDict(
    coarse_x = 0x11111,
    coarse_y = 0x11111 << 5,
    nametable_x = 1 << 10,
    nametable_y = 1 << 11,
    fine_y = 0x111 << 12,
    unused = 1 << 15,
)

def set_flag(reg, reg2, flag):
    #reg[flag] = reg2[flag]
    reg |= reg2 & flag
    reg &= reg2 | ~flag
    return reg

class PPU(Device):
    def __init__(self, name: str=None) -> None:
        super().__init__(name=name)

        self.tblName = mtx(0, (2, 1024))
        self.tblPattern = mtx(0, (2, 4096))
        self.tblPalette = mtx(size=32)
        self.tblPalette = list(range(32))

        self.palScreen = palScreen
        self.sprScreen = mtx(0, (256, 240, 3))
        self.sprNameTable = mtx(0, (2, 256, 240))
        self.sprPatternTable = mtx(0, (2, 128, 128, 3))
        self.frame_complete = False
        self.scanline = 0
        self.cycle = 0
        self.cartridge:Cartridge = None
        self.engine = Engine()
        self.status = u8()
        self.mask = u8()
        self.control = u8()
        self.vram_addr = u16()
        self.tram_addr = u16()
        self.fine_x = u8()
        self.address_latch = 0
        self.ppu_data_buffer = u8()
        self.bg_next_tile_id = u8()
        self.bg_next_tile_attrib = u8()
        self.bg_next_tile_lsb = u8()
        self.bg_next_tile_msb = u8()
        self.bg_shifter_pattern_lo = u16()
        self.bg_shifter_pattern_hi = u16()
        self.bg_shifter_attrib_lo = u16()
        self.bg_shifter_attrib_hi = u16()
        self.nmi = False

    def read(self, addr: t16) -> t8:
        assert_u16(addr)
        data = 0x0
        if addr == 0x0002:
            data = (self.status & 0xE0) | (self.ppu_data_buffer & 0x1F)
            self.status &= u8(~STATUS_FLAG.vertical_blank)
            self.address_latch = 0
        if addr == 0x0007:
            data = self.ppu_data_buffer
            self.ppu_data_buffer = self.ppuRead(self.vram_addr)
            if self.vram_addr >= 0x3F00:
                data = self.ppu_data_buffer
            self.vram_addr += (32 if self.control & CONTROL_FLAG.increment_mode else 1)
        return data
    
    def write(self, addr: t16, data: t8) -> None:
        assert_u16(addr)
        if addr == 0x0000:
            self.control = data
            set_flag(self.tram_addr, self.control, CONTROL_FLAG.nametable_x | CONTROL_FLAG.nametable_Y)
        if addr == 0x0001:
            self.mask = data
        if addr == 0x0005:
            if self.address_latch == 0:
                self.fine_x = data & 0x07
                set_flag(self.tram_addr, data >> 3, LOOPY_FLAG.coarse_x)
                self.address_latch = 1
            else:
                set_flag(self.tram_addr, u16(data) & 0x07 << 12, LOOPY_FLAG.fine_y)
                set_flag(self.tram_addr, u16(data) >> 3 << 5, LOOPY_FLAG.coarse_y)
                self.address_latch = 0
        if addr == 0x0006:
            if self.address_latch == 0:
                self.tram_addr = (u16(data) & 0x3F) << 8 | self.tram_addr & 0x00FF
                self.address_latch = 1
            else:
                self.tram_addr = (self.tram_addr & 0xFF00) | data
                self.vram_addr = self.tram_addr
                self.address_latch = 0
        if addr == 0x0007:
            self.ppuWrite(self.vram_addr, data)
            self.vram_addr += 32 if self.control & CONTROL_FLAG.increment_mode else 1

    def ppuRead(self, addr: t16) -> t8:
        assert_u16(addr)
        addr &= 0x3FFF
        data = self.cartridge.ppuRead(addr=addr)
        if data is not False:
            pass
        elif 0x0000 <= addr <= 0x1FFF:
            data = self.tblPattern[(addr & 0x1000) >> 12][addr & 0x0FFF]
        elif 0x2000 <= addr <= 0x3EFF:
            addr &= 0x0FFF
            if self.cartridge.mirror == VERTICAL:
                if 0x0000 <= addr <= 0x03FF:
                    data = self.tblName[0][addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data = self.tblName[1][addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data = self.tblName[0][addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data = self.tblName[1][addr & 0x03FF]
            elif self.cartridge.mirror == HORIZONTAL:
                if 0x0000 <= addr <= 0x03FF:
                    data = self.tblName[0][addr & 0x03FF]
                if 0x0400 <= addr <= 0x07FF:
                    data = self.tblName[0][addr & 0x03FF]
                if 0x0800 <= addr <= 0x0BFF:
                    data = self.tblName[1][addr & 0x03FF]
                if 0x0C00 <= addr <= 0x0FFF:
                    data = self.tblName[1][addr & 0x03FF]
        elif 0x3F00 < addr < 0x3FFF:
            addr &= 0x001F
            if addr == 0x0010: addr = 0x0000
            if addr == 0x0014: addr = 0x0004
            if addr == 0x0018: addr = 0x0008
            if addr == 0x001C: addr = 0x000C
            data = self.tblPalette[addr] & (0x30 if self.mask & MASK_FLAG.grayscale else 0x3F)
        return data

    def ppuWrite(self, addr: t16, data: t8) -> None:
        assert_u16(addr)
        logger.debug('ppuWrite, addr=0x{:04x}, data=0x{:02x}', addr, data)
        addr = addr & 0x3FFF
        if self.cartridge.ppuWrite(addr=addr, data=data):
            return
        elif 0x0000 <= addr <= 0x1FFF:
            self.tblPattern[(addr & 0x1000) >> 12, addr & 0x0FFF] = data
        elif 0x2000 <= addr <= 0x3EFF:
            addr &= 0x0FFF
            if self.cartridge.mirror == VERTICAL:
                if 0x0000 <= addr <= 0x03FF:
                    self.tblName[0][addr & 0x03FF] = data
                if 0x0400 <= addr <= 0x07FF:
                    self.tblName[1][addr & 0x03FF] = data
                if 0x0800 <= addr <= 0x0BFF:
                    self.tblName[0][addr & 0x03FF] = data
                if 0x0C00 <= addr <= 0x0FFF:
                    self.tblName[1][addr & 0x03FF] = data
            elif self.cartridge.mirror == HORIZONTAL:
                if 0x0000 <= addr <= 0x03FF:
                    self.tblName[0][addr & 0x03FF] = data
                if 0x0400 <= addr <= 0x07FF:
                    self.tblName[0][addr & 0x03FF] = data
                if 0x0800 <= addr <= 0x0BFF:
                    self.tblName[1][addr & 0x03FF] = data
                if 0x0C00 <= addr <= 0x0FFF:
                    self.tblName[1][addr & 0x03FF] = data
        elif 0x3F00 <= addr <= 0x3FFF:
            addr &= 0x001F
            if addr == 0x0010: addr = 0x0000
            if addr == 0x0014: addr = 0x0004
            if addr == 0x0018: addr = 0x0008
            if addr == 0x001C: addr = 0x000C
            self.tblPalette[addr] = data
        return data

    def ConnectCartridge(self, cartridge:Cartridge) -> None:
        self.cartridge = cartridge

    
    def IncrementScrollX(self):
        if self.mask & (MASK_FLAG.render_background | MASK_FLAG.render_sprites):
            if self.vram_addr & LOOPY_FLAG.coarse_x == 31:
                set_flag(self.vram_addr, 0, LOOPY_FLAG.coarse_x)
                set_flag(self.vram_addr, ~self.vram_addr, LOOPY_FLAG.nametable_x)
            else:
                self.vram_addr += 1
    
    def IncrementScrollY(self):
        if self.mask & (MASK_FLAG.render_background | MASK_FLAG.render_sprites):
            if self.vram_addr & LOOPY_FLAG.fine_y  < 7 << 12:
                self.vram_addr += 1<<12
            else:
                self.vram_addr &= ~LOOPY_FLAG.fine_y
                if self.vram_addr & LOOPY_FLAG.coarse_y == 29 << 5:
                    self.vram_addr &= ~LOOPY_FLAG.coarse_y
                    set_flag(self.vram_addr, ~self.vram_addr, LOOPY_FLAG.nametable_y)
                elif self.vram_addr & LOOPY_FLAG.coarse_y == 31 << 5:
                    self.vram_addr &= ~LOOPY_FLAG.coarse_y
                else:
                    self.vram_addr += 1 << 5
    
    def TransferAddressX(self):
        if self.mask & (MASK_FLAG.render_background | MASK_FLAG.render_sprites):
            set_flag(self.vram_addr, self.tram_addr, LOOPY_FLAG.nametable_x | LOOPY_FLAG.coarse_x)

    def TransferAddressY(self):
        if self.mask & (MASK_FLAG.render_background | MASK_FLAG.render_sprites):
            set_flag(self.vram_addr, self.tram_addr, 
                LOOPY_FLAG.nametable_y | LOOPY_FLAG.coarse_y, LOOPY_FLAG.fine_y)
    
    def LoadBackgroundShifters(self):
        self.bg_shifter_pattern_lo = (self.bg_shifter_pattern_lo & 0xFF00) | self.bg_next_tile_lsb
        self.bg_shifter_pattern_hi = (self.bg_shifter_pattern_hi & 0xFF00) | self.bg_next_tile_msb
        self.bg_shifter_attrib_lo  = (self.bg_shifter_attrib_lo & 0xFF00) | (0xFF if self.bg_next_tile_attrib & 0b01 else 0x00)
        self.bg_shifter_attrib_hi  = (self.bg_shifter_attrib_hi & 0xFF00) | (0xFF if self.bg_next_tile_attrib & 0b10 else 0x00)

    def UpdateShifters(self):
        if self.mask & MASK_FLAG.render_background:
            self.bg_shifter_pattern_lo <<= 1
            self.bg_shifter_pattern_hi <<= 1
            self.bg_shifter_attrib_lo <<= 1
            self.bg_shifter_attrib_hi <<= 1

    def clock(self) -> None:

        if self.scanline >= -1 and self.scanline < 240:
            if self.scanline == 0 and self.cycle == 0:
                self.cycle = 1
            if self.scanline == -1 and self.cycle == 1:
                self.status &= u8(~STATUS_FLAG.vertical_blank)
            if (self.cycle >= 2 and self.cycle < 258) or (self.cycle >= 321 and self.cycle < 338):
                self.UpdateShifters()

                if (self.cycle - 1) & 3 == 0:
                    self.LoadBackgroundShifters()
                    self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr & 0x0FFF))
                elif (self.cycle - 1) & 3 == 2:
                    self.bg_next_tile_attrib = self.ppuRead(0x23C0
                        | (self.vram_addr & (LOOPY_FLAG.nametable_y | LOOPY_FLAG.nametable_x))
                        | ((self.vram_addr & LOOPY_FLAG.coarse_y) >> 7) << 3 
                        | (self.vram_addr & LOOPY_FLAG.coarse_x) >> 2)
                    
                    if self.vram_addr & 0x02 << 5:
                        self.bg_next_tile_attrib >>= 4
                    if self.vram_addr & 0x02:
                        self.bg_next_tile_attrib >>= 2
                    self.bg_next_tile_attrib &= 0x03

                elif (self.cycle - 1) & 3 == 4:
                    self.bg_next_tile_lsb = self.ppuRead((self.control & CONTROL_FLAG.pattern_background << 8) 
                        + (u16(self.bg_next_tile_id) << 4) 
                        + (self.vram_addr & LOOPY_FLAG.fine_y) >> 12)

                elif (self.cycle - 1) & 3 == 6:
                    self.bg_next_tile_msb = self.ppuRead((self.control & CONTROL_FLAG.pattern_background << 8) 
                        + (u16(self.bg_next_tile_id) << 4) 
                        + ((self.vram_addr & LOOPY_FLAG.fine_y) >> 12) + 8)

                elif (self.cycle - 1) & 3 == 7:
                    self.IncrementScrollX()

            if self.cycle == 256:
                self.IncrementScrollY()

            if self.cycle == 257:
                self.LoadBackgroundShifters()
                self.TransferAddressX()

            if self.cycle == 338 or self.cycle == 340:
                self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr & 0x0FFF))

            if self.scanline == -1 and self.cycle >= 280 and self.cycle < 305:
                self.TransferAddressY()

        if self.scanline == 240:
            pass

        if self.scanline >= 241 and self.scanline < 261:
            if self.scanline == 241 and self.cycle == 1:
                self.status |= STATUS_FLAG.vertical_blank
                if self.control & CONTROL_FLAG.enable_nmi:
                    self.nmi = True

        bg_pixel = u8(0x00)
        bg_palette = u8(0x00)
        if self.mask & MASK_FLAG.render_background:
            bit_mux = u16(0x8000) >> self.fine_x
            p0_pixel = (self.bg_shifter_pattern_lo & bit_mux) > 0
            p1_pixel = (self.bg_shifter_pattern_hi & bit_mux) > 0
            bg_pixel = (p1_pixel << 1) | p0_pixel
            bg_pal0 = (self.bg_shifter_attrib_lo & bit_mux) > 0
            bg_pal1 = (self.bg_shifter_attrib_hi & bit_mux) > 0
            bg_palette = (bg_pal1 << 1) | bg_pal0
        self.engine.set_pixel(self.cycle - 1, self.scanline, self.GetColourFromPaletteRam(bg_palette, bg_pixel))

        self.cycle += 1
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1
            if self.scanline >= 261:
                self.engine.update()
                self.scanline = -1
                self.frame_complete = True

    def GetPatternTable(self, i:int, palette:int) -> int:
        for nTileY in range(16):
            for nTileX in range(16):
                nOffset = nTileY * 256 + nTileX * 16
                for row in range(8):
                    tile_lsb = self.ppuRead(i * 0x1000 + nOffset + row + 0x0000)
                    tile_msb = self.ppuRead(i * 0x1000 + nOffset + row + 0x0008)
                    for col in range(8):
                        pixel = (tile_lsb & 0x01) + (tile_msb & 0x01)
                        tile_lsb >>= 1
                        tile_msb >>= 1
                        self.sprPatternTable[i][nTileX * 8 + (7 - col)][nTileY * 8 + row] = self.GetColourFromPaletteRam(palette, pixel)
        return self.sprPatternTable[i]
    
    def GetColourFromPaletteRam(self, palette, pixel):
        return self.palScreen[self.ppuRead(0x3F00 + (palette << 2) + pixel) & 0x3F]

    def reset(self) -> None:
        self.fine_x = u8()
        self.address_latch = 0
        self.ppu_data_buffer = u8()
        self.scanline = 0
        self.cycle = 0
        self.bg_next_tile_id = u8()
        self.bg_next_tile_attrib = u8()
        self.bg_next_tile_lsb = u8()
        self.bg_next_tile_msb = u8()
        self.bg_shifter_pattern_lo = u16()
        self.bg_shifter_pattern_hi = u16()
        self.bg_shifter_attrib_lo = u16()
        self.bg_shifter_attrib_hi = u16()
        self.status = u8()
        self.mask = u8()
        self.control = u8()
        self.vram_addr = u16()
        self.tram_addr = u16()


if __name__ == '__main__':
    ppu = PPU()
    while not ppu.engine.finished:
        ppu.clock()

