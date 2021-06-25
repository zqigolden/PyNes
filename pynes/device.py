from abc import ABC
from pynes.bits import t16, t8

class Device(ABC):
    def __init__(self, name:str='') -> None:
        super().__init__()
        self.name = name if name else f'{self.__class__.__name__}@{id(self)}'
    
    def __str__(self, exist_devices=None) -> str:
        r = []
        for attr_name, val in self.__dict__.items():
            if isinstance(val, Device):
                if exist_devices and id(val) in exist_devices:
                    r.append((attr_name, val.name))
                else:
                    if exist_devices is None:
                        exist_devices = {id(self)}
                    exist_devices.add(id(val))
                    r.append((attr_name, val.__str__(exist_devices=exist_devices)))
            elif isinstance(val, (int, bool)):
                r.append((attr_name, val))
        msg = ", ".join([f'{i}={j}' for i, j in r])
        return f'{self.name}({msg})'

    def read(self, addr:t16)->t8:
        raise NotImplementedError

    def write(self, addr:t16, data:t8)->None:
        raise NotImplementedError
    
    def reset(self) -> None:
        pass

if __name__ == '__main__':
    print(Device().read(1))