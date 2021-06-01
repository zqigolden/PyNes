from abc import ABC
import numpy as np

class Device(ABC):
    def __init__(self, name:str='') -> None:
        super().__init__()
        self.name = name if name else f'{self.__class__.__name__}@{id(self)}'
    
    def __str__(self) -> str:
        return f'{self.name}({", ".join([n+"="+str(val) for n, val in self.__dict__.items() if isinstance(val, np.ndarray)])})'

    def read(self, addr:np.ndarray)->np.ndarray:
        raise NotImplementedError

    def write(self, addr:np.ndarray, data:np.ndarray)->None:
        raise NotImplementedError

if __name__ == '__main__':
    print(Device().read(1))