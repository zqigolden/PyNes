from bits import uint8, uint16
import numpy as np
from device import Device
class RAM(Device):
    def __init__(self, size=1 << 13, dummy=False, name: str='') -> None:
        super().__init__(name=name)
        self.size = size
        self.memory = uint8(0, self.size)
        if dummy:
            self.dummy()

    def reset(self) -> None:
        self.memory[...] = 0

    def dummy(self) -> None:
        self.memory = np.arange(self.size, dtype=np.uint8)

    def read(self, addr: np.ndarray) -> np.ndarray:
        return self.memory[addr]

    def write(self, addr: np.ndarray, data: np.ndarray) -> None:
        self.memory[addr] = data

if __name__ == '__main__':
    ram = RAM()
    addr = uint16(0xff)
    data = uint8(0x13)
    ram.write(addr=addr, data=data)
    print(ram.read(addr=addr))
    ram.reset()
    print(ram.read(addr))
    print(ram)
    ram.dummy()
    print(ram, len(ram.memory))