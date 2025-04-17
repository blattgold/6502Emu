from abc import ABC, abstractmethod
from typing import final
from cpu import CPU

class Instruction(ABC):
    def __init__(self, cpu: CPU):
        self._cpu = cpu
        self._clock_cycles = 2
        self._bytes = 1
        self._debug = True
        self._addr = -1

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def _run(self):
        pass

    @final
    def __call__(self) -> None:
        if self._bytes == 1:
            pass
        elif self._bytes == 2: 
            self._addr = self._cpu.fetch(1)
        else:
            self._addr = self._cpu.fetch_two(1)

        self._run()
        self._cpu.pc += self._bytes
        self._cpu.clock_cycles = self._clock_cycles

        if self._debug: 
            print(self)

class InstructionZeroPage(Instruction):
    def __init__(self, cpu: CPU):
        super().__init__(cpu)
        self._clock_cycles = 3
        self._bytes = 2

    @final
    def _get_val_at_addr(self) -> int:
        return self._cpu.memory.get_byte(self._addr)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._cpu.memory.set_byte(self._addr, val)

class InstructionZeroPageIndexed(Instruction):
    def __init__(self, cpu: CPU, r_index: str):
        assert(r_index == "X" or r_index == "Y")
        super().__init__(cpu)
        self._r_index = r_index
        self._clock_cycles = 4
        self._bytes = 2
    
    @final
    def _get_val_at_addr(self) -> int:
        return self._cpu.memory.get_byte((self._addr + self._cpu.get_register(self._r_index)) &0xFF)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._cpu.memory.set_byte((self._addr + self._cpu.get_register(self._r_index)) &0xFF, val)
    
class InstructionAbsolute(Instruction):
    def __init__(self, cpu: CPU):
        super().__init__(cpu)
        self._clock_cycles = 4
        self._bytes = 3
    
    @final
    def _get_val_at_addr(self) -> int:
        return self._cpu.memory.get_two_bytes(self._addr)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._cpu.memory.set_byte(self._addr, val)

class InstructionAbsoluteIndexed(Instruction):
    def __init__(self, cpu: CPU, r_index: str):
        assert(r_index == "X" or r_index == "Y")
        super().__init__(cpu)
        self._r_index = r_index
        self._clock_cycles = 5
        self._bytes = 3
    
    @final
    def _get_val_at_addr(self) -> int:
        return self._cpu.memory.get_byte((self._addr + self._cpu.get_register(self._r_index)) &0xFFFF)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._cpu.memory.set_byte((self._addr + self._cpu.get_register(self._r_index)) &0xFFFF, val)