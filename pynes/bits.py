from typing import List, Tuple

def uint8(init_val: int = 0) -> int:
    return init_val & 0xFF

def uint16(init_val: int = 0, size:int=1) -> int:
    return init_val & 0xFFFF

def mtx(init_val:int=0, size:Tuple[int]=(1,)) -> List:
    if isinstance(size, int):
        return [init_val] * size
    if len(size) == 1:
        return [init_val] * size[0]
    return [mtx(init_val, size[1:]) for _ in range(size[0])]

def assert_u16(d:int)->None:
    # return
    assert 0x0000 <= d <= 0xffff
def assert_u8(d:int)->None:
    # return
    assert 0x00 <= d <= 0xff

def flipbyte(b):
    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
    b = (b & 0xCC) >> 2 | (b & 0x33) << 2
    b = (b & 0xAA) >> 1 | (b & 0x55) << 1
    return b

u16 = uint16
u8 = uint8

t16 = int
t8 = int