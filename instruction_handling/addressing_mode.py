from abc import ABC, abstractmethod

class AddressingModeBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_effective_address(self, addr):
        pass

class AddressingModeZeroPage(AddressingModeBase):
    def get_effective_address(self, addr):
        return addr

class AddressingModeZeroPageIndexed(AddressingModeBase):
    def get_effective_address(self, addr, index):
        return (addr + index) &0xFF