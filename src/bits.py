import numpy as np
from numpy.lib.arraysetops import isin

def uint8(init_val: int = 0, size:int=1) -> np.ndarray:
    if isinstance(init_val, np.ndarray):
        init_val = init_val[0]
    return np.array([init_val]*size, dtype=np.uint8)

def uint16(init_val: int = 0, size:int=1) -> np.ndarray:
    if isinstance(init_val, np.ndarray):
        init_val = init_val[0]
    return np.array([init_val]*size, dtype=np.uint16)

u16 = uint16
u8 = uint8