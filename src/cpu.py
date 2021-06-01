from typing import Any, Optional
import easydict
import numpy as np
from numpy.lib.type_check import real
from bits import uint8, uint16, u8, u16
from easydict import EasyDict
from bus import Bus
from device import Device
from ram import RAM

class FLAGS6502:
    C = uint8(1 << 0)   # Carry Bit
    Z = uint8(1 << 1)   # Zero
    I = uint8(1 << 2)   # Disable Interrupts
    D = uint8(1 << 3)   # Decimal Mode (unused in this implementation)
    B = uint8(1 << 4)   # Break
    U = uint8(1 << 5)   # Unused
    V = uint8(1 << 6)   # Overflow
    N = uint8(1 << 7)   # Negative

lookup = '''
BRK,BRK,IMM,7 ORA,ORA,IZX,6 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,3 ORA,ORA,ZP0,3 ASL,ASL,ZP0,5 ???,XXX,IMP,5 PHP,PHP,IMP,3 ORA,ORA,IMM,2 ASL,ASL,IMP,2 ???,XXX,IMP,2 ???,NOP,IMP,4 ORA,ORA,ABS,4 ASL,ASL,ABS,6 ???,XXX,IMP,6
BPL,BPL,REL,2 ORA,ORA,IZY,5 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,4 ORA,ORA,ZPX,4 ASL,ASL,ZPX,6 ???,XXX,IMP,6 CLC,CLC,IMP,2 ORA,ORA,ABY,4 ???,NOP,IMP,2 ???,XXX,IMP,7 ???,NOP,IMP,4 ORA,ORA,ABX,4 ASL,ASL,ABX,7 ???,XXX,IMP,7
JSR,JSR,ABS,6 AND,AND,IZX,6 ???,XXX,IMP,2 ???,XXX,IMP,8 BIT,BIT,ZP0,3 AND,AND,ZP0,3 ROL,ROL,ZP0,5 ???,XXX,IMP,5 PLP,PLP,IMP,4 AND,AND,IMM,2 ROL,ROL,IMP,2 ???,XXX,IMP,2 BIT,BIT,ABS,4 AND,AND,ABS,4 ROL,ROL,ABS,6 ???,XXX,IMP,6
BMI,BMI,REL,2 AND,AND,IZY,5 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,4 AND,AND,ZPX,4 ROL,ROL,ZPX,6 ???,XXX,IMP,6 SEC,SEC,IMP,2 AND,AND,ABY,4 ???,NOP,IMP,2 ???,XXX,IMP,7 ???,NOP,IMP,4 AND,AND,ABX,4 ROL,ROL,ABX,7 ???,XXX,IMP,7
RTI,RTI,IMP,6 EOR,EOR,IZX,6 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,3 EOR,EOR,ZP0,3 LSR,LSR,ZP0,5 ???,XXX,IMP,5 PHA,PHA,IMP,3 EOR,EOR,IMM,2 LSR,LSR,IMP,2 ???,XXX,IMP,2 JMP,JMP,ABS,3 EOR,EOR,ABS,4 LSR,LSR,ABS,6 ???,XXX,IMP,6
BVC,BVC,REL,2 EOR,EOR,IZY,5 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,4 EOR,EOR,ZPX,4 LSR,LSR,ZPX,6 ???,XXX,IMP,6 CLI,CLI,IMP,2 EOR,EOR,ABY,4 ???,NOP,IMP,2 ???,XXX,IMP,7 ???,NOP,IMP,4 EOR,EOR,ABX,4 LSR,LSR,ABX,7 ???,XXX,IMP,7
RTS,RTS,IMP,6 ADC,ADC,IZX,6 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,3 ADC,ADC,ZP0,3 ROR,ROR,ZP0,5 ???,XXX,IMP,5 PLA,PLA,IMP,4 ADC,ADC,IMM,2 ROR,ROR,IMP,2 ???,XXX,IMP,2 JMP,JMP,IND,5 ADC,ADC,ABS,4 ROR,ROR,ABS,6 ???,XXX,IMP,6
BVS,BVS,REL,2 ADC,ADC,IZY,5 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,4 ADC,ADC,ZPX,4 ROR,ROR,ZPX,6 ???,XXX,IMP,6 SEI,SEI,IMP,2 ADC,ADC,ABY,4 ???,NOP,IMP,2 ???,XXX,IMP,7 ???,NOP,IMP,4 ADC,ADC,ABX,4 ROR,ROR,ABX,7 ???,XXX,IMP,7
???,NOP,IMP,2 STA,STA,IZX,6 ???,NOP,IMP,2 ???,XXX,IMP,6 STY,STY,ZP0,3 STA,STA,ZP0,3 STX,STX,ZP0,3 ???,XXX,IMP,3 DEY,DEY,IMP,2 ???,NOP,IMP,2 TXA,TXA,IMP,2 ???,XXX,IMP,2 STY,STY,ABS,4 STA,STA,ABS,4 STX,STX,ABS,4 ???,XXX,IMP,4
BCC,BCC,REL,2 STA,STA,IZY,6 ???,XXX,IMP,2 ???,XXX,IMP,6 STY,STY,ZPX,4 STA,STA,ZPX,4 STX,STX,ZPY,4 ???,XXX,IMP,4 TYA,TYA,IMP,2 STA,STA,ABY,5 TXS,TXS,IMP,2 ???,XXX,IMP,5 ???,NOP,IMP,5 STA,STA,ABX,5 ???,XXX,IMP,5 ???,XXX,IMP,5
LDY,LDY,IMM,2 LDA,LDA,IZX,6 LDX,LDX,IMM,2 ???,XXX,IMP,6 LDY,LDY,ZP0,3 LDA,LDA,ZP0,3 LDX,LDX,ZP0,3 ???,XXX,IMP,3 TAY,TAY,IMP,2 LDA,LDA,IMM,2 TAX,TAX,IMP,2 ???,XXX,IMP,2 LDY,LDY,ABS,4 LDA,LDA,ABS,4 LDX,LDX,ABS,4 ???,XXX,IMP,4
BCS,BCS,REL,2 LDA,LDA,IZY,5 ???,XXX,IMP,2 ???,XXX,IMP,5 LDY,LDY,ZPX,4 LDA,LDA,ZPX,4 LDX,LDX,ZPY,4 ???,XXX,IMP,4 CLV,CLV,IMP,2 LDA,LDA,ABY,4 TSX,TSX,IMP,2 ???,XXX,IMP,4 LDY,LDY,ABX,4 LDA,LDA,ABX,4 LDX,LDX,ABY,4 ???,XXX,IMP,4
CPY,CPY,IMM,2 CMP,CMP,IZX,6 ???,NOP,IMP,2 ???,XXX,IMP,8 CPY,CPY,ZP0,3 CMP,CMP,ZP0,3 DEC,DEC,ZP0,5 ???,XXX,IMP,5 INY,INY,IMP,2 CMP,CMP,IMM,2 DEX,DEX,IMP,2 ???,XXX,IMP,2 CPY,CPY,ABS,4 CMP,CMP,ABS,4 DEC,DEC,ABS,6 ???,XXX,IMP,6
BNE,BNE,REL,2 CMP,CMP,IZY,5 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,4 CMP,CMP,ZPX,4 DEC,DEC,ZPX,6 ???,XXX,IMP,6 CLD,CLD,IMP,2 CMP,CMP,ABY,4 NOP,NOP,IMP,2 ???,XXX,IMP,7 ???,NOP,IMP,4 CMP,CMP,ABX,4 DEC,DEC,ABX,7 ???,XXX,IMP,7
CPX,CPX,IMM,2 SBC,SBC,IZX,6 ???,NOP,IMP,2 ???,XXX,IMP,8 CPX,CPX,ZP0,3 SBC,SBC,ZP0,3 INC,INC,ZP0,5 ???,XXX,IMP,5 INX,INX,IMP,2 SBC,SBC,IMM,2 NOP,NOP,IMP,2 ???,SBC,IMP,2 CPX,CPX,ABS,4 SBC,SBC,ABS,4 INC,INC,ABS,6 ???,XXX,IMP,6
BEQ,BEQ,REL,2 SBC,SBC,IZY,5 ???,XXX,IMP,2 ???,XXX,IMP,8 ???,NOP,IMP,4 SBC,SBC,ZPX,4 INC,INC,ZPX,6 ???,XXX,IMP,6 SED,SED,IMP,2 SBC,SBC,ABY,4 NOP,NOP,IMP,2 ???,XXX,IMP,7 ???,NOP,IMP,4 SBC,SBC,ABX,4 INC,INC,ABX,7 ???,XXX,IMP,7
'''

class CPU(Device):
    def __init__(self, bus:Bus, name:str='') -> None:
        super().__init__(name=name)

        # actrual registers
        self.a = uint8()
        self.x = uint8()
        self.y = uint8()
        self.stkp = uint16()
        self.pc = uint16()
        self.status = uint8()

        # virtual variables
        self.fetched = uint8()
        self.temp = uint16()
        self.addr_abs = uint16()
        self.addr_rel = uint16()
        self.optcode = uint8()
        self.cycles = 0
        self.clock_count = 0

        self.bus = bus
        self.bus.connect(self, None)
        self.read = self.bus.read
        self.write = self.bus.write
        self.lookup = [tuple(i.split(',')) for i in lookup.split()]

    def reset(self)->None:
        addr_abs = uint16(0xFFFC)
        lo = self.read(addr_abs)
        hi = self.read(addr_abs + 1)
        self.pc = uint16() + hi << 8 | lo
        self.a = uint8()
        self.x = uint8()
        self.y = uint8()
        self.stkp = uint16(0xFD)
        self.status = uint16() | FLAGS6502.U
        self.addr_rel = uint16()
        self.addr_abs = uint16()
        self.fetched = uint8()
        self.cycles = 8

    def setFlag(self, flag:Any, val:int) -> None:
        if isinstance(flag, str):
            flag = FLAGS6502.__dict__[flag.upper()]
        if val:
            self.status |= flag
        else:
            self.status &= ~flag

    def getFlag(self, flag:Any) -> int:
        if isinstance(flag, str):
            flag = FLAGS6502.__dict__[flag.upper()]
        return 1 if self.status & flag else 0

    # addressing Modes
    def IMP(self)->int:
        self.fetched = u8(self.a)
        return 0

    def IMM(self)->int:
        self.addr_abs = uint16(self.pc)
        self.pc += 1
        return 0

    def ZP0(self)->int:
        self.addr_abs = uint16(self.read(self.pc))
        self.pc += 1
        return 0

    def ZPX(self)->int:
        self.addr_abs = uint16(self.read(self.pc) + self.x)
        self.pc += 1
        return 0

    def ZPY(self)->int:
        self.addr_abs = uint16(self.read(self.pc) + self.y)
        self.pc += 1
        return 0

    def REL(self)->int:
        self.addr_rel = u16(self.read(self.pc))
        self.pc += 1
        if self.addr_rel & 0x80:
            self.addr_rel |= 0xFF00
        return 0

    def ABS(self)->int:
        lo = self.read(self.pc)
        self.pc += 1
        hi = self.read(self.pc)
        self.addr_abs = uint16(hi << 8 | lo)
        self.pc += 1
        return 0

    def ABX(self)->int:
        self.ABS()
        hi = self.addr_abs & 0xFF
        self.addr_abs += self.x
        if self.addr_abs & 0xFF != hi:
            return 1
        return 0

    def ABY(self)->int:
        self.ABS()
        hi = self.addr_abs & 0xFF
        self.addr_abs += self.y
        if self.addr_abs & 0xFF != hi:
            return 1
        return 0

    def IND(self)->int:
        lo = self.read(self.pc)
        self.pc += 1
        hi = self.read(self.pc + 1)
        self.pc += 1
        ptr = hi << 8 | lo
        if lo == 0xff:
            self.addr_abs = (self.read(ptr & 0xff00) << 8) | self.read(ptr + 0)
        else:
            self.addr_abs = (self.read(ptr + 1) << 8) | self.read(ptr + 0)
        return 0


    def IZX(self)->int:
        t = u16(self.read(self.pc))
        self.pc += 1
        lo = self.read((t + self.x) & 0x00FF)
        hi = self.read((t + self.x + 1) & 0x00FF)
        self.addr_abs = (hi << 8) | lo
        return 0

    def IZY(self)->int:
        t = u16(self.read(self.pc))
        self.pc += 1
        lo = self.read(t & 0x00FF)
        hi = self.read((t + 1) & 0x00FF)
        self.addr_abs = (hi << 8) | lo
        self.addr_abs += self.y
        if self.addr_abs & 0xff00 != hi << 8:
            return 1
        return 0

    def fetch(self) -> np.ndarray:
        if not self.lookup[self.optcode][0] == 'IMP':
            self.fetched = self.read(self.addr_abs)
        return self.fetched[:]

    def ADC(self) -> int:
        self.fetch()
        self.temp = u16(self.a) + self.fetched + self.getFlag('C')
        self.setFlag('C', self.temp > 255)
        self.setFlag('Z', self.temp & 0x00FF == 0)
        self.setFlag('V', (~(u16(self.a) ^ self.fetched) & (u16(self.a) ^ self.temp)) & 0x0080)
        self.setFlag('N', self.temp & 0x80)
        self.a = u8(self.temp)
        return 1

    def SBC(self) -> int:
        self.fetch()
        val = self.fetched ^ 0x00FF
        self.temp = u16(self.a) + val + self.getFlag('C')
        self.setFlag('C', self.temp > 255)
        self.setFlag('Z', self.temp & 0x00FF == 0)
        self.setFlag('V', (~(u16(self.a) ^ self.fetched) & (u16(self.a) ^ self.temp)) & 0x0080)
        self.setFlag('N', self.temp & 0x80)
        self.a = u8(self.temp)
        return 1

    def AND(self) -> int:
            self.fetch()
            self.a &= self.fetched
            self.setFlag('Z', self.a == 0x00)
            self.setFlag('N', self.a & 0x80)
            return 1


if __name__ == '__main__':
    bus = Bus()
    bus.connect(RAM(size=65536, dummy=True), (0x0000, 0xFFFF))
    cpu = CPU(bus)
    cpu.reset()
    print(cpu, cpu.getFlag('Z'))
    cpu.setFlag('Z', 1)
    print(cpu, cpu.getFlag('Z'))
    print(cpu.lookup)