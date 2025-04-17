from abc import ABC, abstractmethod
from ..cpu import CPU

class Instruction(ABC):
    def __init__(self, cpu: CPU):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def run(self):
        pass

class InstructionImplied(Instruction):
    def __init__(self, cpu: CPU):
        pass
    def run(self):
        pass

class InstructionImmediate(Instruction):
    def __init__(self, cpu: CPU):
        pass
    def run(self):
        pass