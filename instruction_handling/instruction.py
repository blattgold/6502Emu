from abc import ABC, abstractmethod
from typing import final
from cpu import CPU

class Instruction(ABC):
    def __init__(self, cpu: CPU):
        self._cpu = cpu
        self.clock_cycles_default = 2
        self._bytes = 1
        self._addr = 0

        self._debug = True

    @property
    def clock_cycles_default(self):
        return self._clock_cycles_default
    
    @clock_cycles_default.setter
    def clock_cycles_default(self, val):
        self._clock_cycles_default = val
        self._clock_cycles = val
    
    @property
    def clock_cycles(self):
        return self._clock_cycles
    
    @clock_cycles.setter
    def clock_cycles(self, val):
        self._clock_cycles = val

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def _run(self):
        pass

    @final
    def __call__(self) -> None:
        self.clock_cycles = self._clock_cycles_default

        if self._bytes == 1:
            pass
        elif self._bytes == 2: 
            self._addr = self._cpu.fetch(1)
        else:
            self._addr = self._cpu.fetch_two(1)

        self._run()
        self._cpu.pc += self._bytes
        self._cpu.clock_cycles += self._clock_cycles

        if self._debug: 
            print(self)

class InstructionZeroPage(Instruction):
    def __init__(self, cpu: CPU):
        super().__init__(cpu)
        self.clock_cycles_default = 3
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
        self.clock_cycles_default = 4
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
        self.clock_cycles_default = 4
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
        self.clock_cycles_default = 5
        self._bytes = 3
    
    @final
    def _get_val_at_addr(self) -> int:
        return self._cpu.memory.get_byte((self._addr + self._cpu.get_register(self._r_index)) &0xFFFF)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._cpu.memory.set_byte((self._addr + self._cpu.get_register(self._r_index)) &0xFFFF, val)

class InstructionIndirectIndexed(Instruction):
    def __init__(self, cpu: CPU, r_index: str):
        assert(r_index == "X" or r_index == "Y")
        super().__init__(cpu)
        self._r_index = r_index
        self.clock_cycles_default = 6
        self._bytes = 2
    
    @final
    def _make_full_addr_y(self) -> None:
        addr_lo = self._addr
        addr_hi = (addr_lo + 1) &0xFF
        addr_pre_index = (addr_hi << 8) | addr_lo
        self._addr = (addr_pre_index + self._cpu.get_register("Y")) &0xFFFF

    @final
    def _make_full_addr_x(self) -> None:
        addr_lo = (self._addr + self._cpu.get_register("X")) &0xFF
        addr_hi = (addr_lo + 1) &0xFF
        self._addr = (addr_hi << 8) | addr_lo

    @final
    def _get_val_at_addr(self) -> int:
        if self._r_index == "X": 
            self._make_full_addr_x()
        else:
            self._make_full_addr_y()
        return self._cpu.memory.get_byte(self._addr)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        if self._r_index == "X": 
            self._make_full_addr_x()
        else:
            self._make_full_addr_y()
        self._cpu.memory.set_byte(self._addr, val)