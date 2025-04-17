from abc import ABC, abstractmethod
from typing import final
from cpu import CPU

class Instruction(ABC):
    def __init__(self, cpu: CPU):
        self._cpu = cpu
        self._clock_cycles = 2
        self._bytes = 1
        self._debug = True

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def _run(self):
        pass

    @final
    def __call__(self) -> None:
        self._run()
        self._cpu.pc += self._bytes
        self._cpu.clock_cycles = self._clock_cycles
        if self._debug: print(self)

class InstructionZeroPage(Instruction):
    def __init__(self, cpu: CPU):
        super().__init__(cpu)
        self._addr = 0
        self._clock_cycles = 3
        self._bytes = 2

    @final
    def _get_memory_value(self) -> int:
        return self._cpu.memory.getByte(self._addr)
    
    @final
    def _set_memory_value(self, val) -> None:
        self._cpu.memory.setByte(self._addr, val)

class InstructionZeroPageIndexed(Instruction):
    def __init__(self, cpu: CPU, r_index: str):
        assert(r_index == "X" or r_index == "Y")
        super().__init__(cpu)
        self._addr = 0
        self._r_index = r_index
        self._clock_cycles = 4
        self._bytes = 2
    
    @final
    def _get_memory_value(self) -> int:
        return self._cpu.memory.getByte((self._addr + self._cpu.get_register(self._r_index)) &0xFF)
    
    @final
    def _set_memory_value(self, val) -> None:
        self._cpu.memory.setByte((self._addr + self._cpu.get_register(self._r_index)) &0xFF, val)