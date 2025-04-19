from abc import ABC, abstractmethod

class AddrModeBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_effective_address(self, addr):
        pass

class AddrModeZP(AddressingModeBase):
    def get_effective_address(self, addr):
        return addr

class AddrModeZPI(AddressingModeBase):
    def get_effective_address(self, addr, index):
        return (addr + index) &0xFF