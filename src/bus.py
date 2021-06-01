from typing import Any, Dict, Tuple

from numpy import ndarray
from bits import uint8, uint16

from device import Device
class Bus(Device):
    def __init__(self, address_count:int=16, data_count:int=8, name:str='') -> None:
        super().__init__(name=name)
        self.address_count = address_count
        self.data_count = data_count
        self.read_only = False
        self.devices:Dict[str, Tuple[Tuple[int], Device]] = {}
    
    def __str__(self) -> str:
        return f'{self.name}(address={self._address_lines.to01()}, data={self._data_lines.to01()}, devices={tuple(self.devices.keys())})'

    def connect(self, device:Device, range:Tuple[int], name:str=None) -> None:
        if not name:
            name = device.name
            assert range is None or len(range) == 2 
            for nm, dev in self.devices.items():
                if range and not(range[0] > dev[0][1] or range[1] < dev[0][0]):
                    raise Exception(f'device {name} and {nm} has same addr range !!!')
            self.devices[name] = (range, device)
    
    def disconnect(self, device:Any) -> None:
        if isinstance(device, str):
            del self.devices[device]
        else:
            del self.devices[device.name]

    def read(self, addr:ndarray)->ndarray:
        i_addr = int(addr)
        for name, device in self.devices.items():
            if device[0] and device[0][0] <= i_addr <= device[0][1]:
                return device[1].read(addr)
    
    def write(self, addr:ndarray, data:ndarray)->None:
        i_addr = int(addr)
        for name, device in self.devices.items():
            if device[0][0] <= i_addr <= device[0][1]:
                device[1].write(addr, data)


if __name__ == '__main__':
    print(Bus())
    b1 = Bus(name='bus1')
    b1.connect(Bus(name='bus2'), [0x00, 0xff])
    b1.connect(Bus(name='bus3'), [0x100, 0x1ff])
    #b1.connect(Bus(name='bus4'), [0x1ff, 0x2ff])
    print(b1)
    
