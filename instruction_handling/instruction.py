from abc import ABC, abstractmethod
from typing import final
from cpu_state import CPUState
from memory import Memory

class Instruction(ABC):
    """
    Abstract Base Instruction class
    """
    def __init__(self, cpu_state: CPUState, memory: Memory):
        self._cpu_state = cpu_state
        self._memory = memory
        self.clock_cycles_default = 2
        self._bytes = 1
        self._addr = 0

        self._debug = False

    @property
    def clock_cycles_default(self):
        return self._clock_cycles_default
    
    @clock_cycles_default.setter
    def clock_cycles_default(self, val):
        self._clock_cycles_default = val
    
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
        """
        Instruction get called like functions for simplicity.
        """
        # blank cpu state, we merge it with the cpu state at the end
        self._new_cpu_state = CPUState()
        # sets clock_cycles to it's default value. clock_cycles may be modified to penalize page changes, for example. 
        self.clock_cycles = self._clock_cycles_default

        # fetch address based on instruction length
        if self._bytes == 1:
            pass
        elif self._bytes == 2:
            self._addr = self._memory.get_byte((self._cpu_state.get_by_id("pc") + 1) &0xFFFF)
        else:
            self._addr = self._memory.get_two_bytes((self._cpu_state.get_by_id("pc") + 1) &0xFFFF)

        # this is where the magic happens
        self._run()

        # advance pc, add clock cycles and merge new state to cpu state
        self._new_cpu_state.set_by_id("pc", self._cpu_state.get_by_id("pc") + self._bytes)
        self._new_cpu_state.set_by_id("clock_cycles", self._cpu_state.get_by_id("clock_cycles") + self.clock_cycles)
        self._cpu_state.merge(self._new_cpu_state)

        if self._debug: 
            print(self)

class InstructionZeroPage(Instruction):
    def __init__(self, cpu_state: CPUState, memory: Memory):
        super().__init__(cpu_state, memory)
        self.clock_cycles_default = 3
        self._bytes = 2

    @final
    def _get_val_at_addr(self) -> int:
        return self._memory.get_byte(self._addr)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._memory.set_byte(self._addr, val)

class InstructionZeroPageIndexed(Instruction):
    def __init__(self, cpu_state: CPUState, memory: Memory, r_index: str):
        assert(r_index == "X" or r_index == "Y")
        super().__init__(cpu_state, memory)
        self._r_index = r_index
        self.clock_cycles_default = 4
        self._bytes = 2
    
    @final
    def _get_val_at_addr(self) -> int:
        return self._memory.get_byte((self._addr + self._cpu_state.get_by_id(self._r_index)) &0xFF)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._memory.set_byte((self._addr + self._cpu_state.get_by_id(self._r_index)) &0xFF, val)
    
class InstructionAbsolute(Instruction):
    def __init__(self, cpu_state: CPUState, memory: Memory):
        super().__init__(cpu_state, memory)
        self.clock_cycles_default = 4
        self._bytes = 3
    
    @final
    def _get_val_at_addr(self) -> int:
        return self._memory.get_two_bytes(self._addr)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._memory.set_byte(self._addr, val)

class InstructionAbsoluteIndexed(Instruction):
    def __init__(self, cpu_state: CPUState, memory: Memory, r_index: str):
        assert(r_index == "X" or r_index == "Y")
        super().__init__(cpu_state, memory)
        self._r_index = r_index
        self.clock_cycles_default = 5
        self._bytes = 3
    
    @final
    def _get_val_at_addr(self) -> int:
        return self._memory.get_byte((self._addr + self._cpu_state.get_by_id(self._r_index)) &0xFFFF)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        self._memory.set_byte((self._addr + self._cpu_state.get_by_id(self._r_index)) &0xFFFF, val)

class InstructionIndirectIndexed(Instruction):
    def __init__(self, cpu_state: CPUState, memory: Memory, r_index: str):
        assert(r_index == "X" or r_index == "Y")
        super().__init__(cpu_state, memory)
        self._r_index = r_index
        self.clock_cycles_default = 6
        self._bytes = 2
    
    @final
    def _make_full_addr_y(self) -> None:
        addr_lo = self._addr
        addr_hi = (addr_lo + 1) &0xFF
        addr_pre_index = (addr_hi << 8) | addr_lo
        self._addr = (addr_pre_index + self._cpu_state.get_by_id("Y")) &0xFFFF

    @final
    def _make_full_addr_x(self) -> None:
        addr_lo = (self._addr + self._cpu_state.get_by_id("X")) &0xFF
        addr_hi = (addr_lo + 1) &0xFF
        self._addr = (addr_hi << 8) | addr_lo

    @final
    def _get_val_at_addr(self) -> int:
        if self._r_index == "X": 
            self._make_full_addr_x()
        else:
            self._make_full_addr_y()
        return self._memory.get_byte(self._addr)
    
    @final
    def _set_val_at_addr(self, val: int) -> None:
        if self._r_index == "X": 
            self._make_full_addr_x()
        else:
            self._make_full_addr_y()
        self._memory.set_byte(self._addr, val)