from instruction_handling.instruction import *

class InstructionTransfer(Instruction):
    def __init__(self, cpu: "CPU", r_from: str, r_to: str):
        super().__init__(cpu)
        self._r_from = r_from
        self._r_to = r_to

    def __str__(self) -> str:
        return f"T{self._r_from}{self._r_to}"

    def _set_flags(self, val: int) -> None:
        self._cpu.set_flag("zero", val == 0)
        self._cpu.set_flag("negative", val > 127)

    def _run(self) -> None:
        r_new = self._cpu.get_register(self._r_from)
        self._cpu.set_register(self._r_to, r_new)
        if self._r_to != "S": self._set_flags(r_new)

class InstructionStoreZeroPage(InstructionZeroPage):
    """
    STA, STX, STY
    adressing: ZeroPage
    """
    def __init__(self, cpu: "CPU", r_from: str):
        super().__init__(cpu)
        self._r_from = r_from

    def __str__(self) -> str:
        return f"ST{self._r_from} {hex(self._addr)}"

    def _run(self) -> str:
        new = self._cpu.get_register(self._r_from)
        self._set_val_at_addr(new)

class InstructionStoreZeroPageIndexed(InstructionZeroPageIndexed):
    """
    STA, STX, STY
    addressing: ZeroPage,X or ZeroPage,Y
    """
    def __init__(self, cpu: "CPU", r_from: str, r_index: str):
        super().__init__(cpu, r_index)
        self._r_from = r_from
    
    def __str__(self) -> str:
        return f"ST{self._r_from} {hex(self._addr)},{self._r_index}:{self._cpu.get_register(self._r_index)}"
    
    def _run(self) -> str:
        new = self._cpu.get_register(self._r_from)
        self._set_val_at_addr(new)

class InstructionStoreAbsolute(InstructionAbsolute):
    """
    STA, STX, STY
    adressing: Absolute
    """
    def __init__(self, cpu: "CPU", r_from: str):
        super().__init__(cpu)
        self._r_from = r_from

    def __str__(self) -> str:
        return f"ST{self._r_from} {hex(self._addr)}"

    def _run(self) -> str:
        new = self._cpu.get_register(self._r_from)
        self._set_val_at_addr(new)

class InstructionStoreAbsoluteIndexed(InstructionAbsoluteIndexed):
    """
    STA, STX, STY
    addressing: Absolute,X or Absolute,Y
    """
    def __init__(self, cpu: "CPU", r_from: str, r_index: str):
        super().__init__(cpu, r_index)
        self._r_from = r_from
    
    def __str__(self) -> str:
        return f"ST{self._r_from} {hex(self._addr)},{self._r_index}:{self._cpu.get_register(self._r_index)}"
    
    def _run(self) -> str:
        new = self._cpu.get_register(self._r_from)
        self._set_val_at_addr(new)

class InstructionStoreIndirectIndexed(InstructionIndirectIndexed):
    """
    STA, STX, STY
    addressing: Indirect,X or Indirect,Y
    """
    def __init__(self, cpu: "CPU", r_from: str, r_index: str):
        super().__init__(cpu, r_index)
        self._r_from = r_from
    
    def __str__(self) -> str:
        return f"ST{self._r_from} {hex(self._addr)},{self._r_index}:{self._cpu.get_register(self._r_index)} (indirect)"
    
    def _run(self) -> str:
        new = self._cpu.get_register(self._r_from)
        self._set_val_at_addr(new)