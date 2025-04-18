import time

from memory import Memory
from instruction_handling import transfer as trans

class CPU:
    '''
    CPU class :3
    '''
    def __init__(self, memory):
        self._memory = memory

        self._decodeFunctionLookupTable = {
            # Transfer
            0xAA: trans.InstructionTransfer(self, "A", "X"), # TAX
            0xA8: trans.InstructionTransfer(self, "A", "Y"), # TAY
            0xBA: trans.InstructionTransfer(self, "S", "X"), # TSX
            0x8A: trans.InstructionTransfer(self, "X", "A"), # TXA
            0x9A: trans.InstructionTransfer(self, "X", "S"), # TXS
            0x98: trans.InstructionTransfer(self, "Y", "A"), # TYA
            # Store
            0x86: trans.InstructionStoreZeroPage(self, "X"), # STX (ZP)
            0x84: trans.InstructionStoreZeroPage(self, "Y"), # STY (ZP)
            0x85: trans.InstructionStoreZeroPage(self, "A"), # STA (ZP)
            0x96: trans.InstructionStoreZeroPageIndexed(self, "X", "Y"), # STX,Y (ZP)
            0x94: trans.InstructionStoreZeroPageIndexed(self, "Y", "X"), # STY,X (ZP)
            0x95: trans.InstructionStoreZeroPageIndexed(self, "A", "X"), # STA,X (ZP)
            0x8E: trans.InstructionStoreAbsolute(self, "X"), # STX (Abs)
            0x8C: trans.InstructionStoreAbsolute(self, "Y"), # STY (Abs)
            0x8D: trans.InstructionStoreAbsolute(self, "A"), # STA (Abs)
            0x9D: trans.InstructionStoreAbsoluteIndexed(self, "A", "X"), # STA,X (Abs)
            0x99: trans.InstructionStoreAbsoluteIndexed(self, "A", "Y"), # STA,Y (Abs)
            0x81: trans.InstructionStoreIndirectIndexed(self, "A", "X"), # STA,X (Ind)
            0x91: trans.InstructionStoreIndirectIndexed(self, "A", "Y"), # STA,Y (Ind)
        }
        """
        Maps opcodes to execution functions.
        Parameters are components needed to execute the function.
        Parameters specify a register for some instructions to reduce redundant code.
        - ADCImm requires the cpu registers, which is why it gets a reference to self (the cpu).
        - ADCZeroPage additionally gets a reference to the memory because it operates on it.
        - LDAAbsoluteIndexed additionally takes a String of the Register to index with (X or Y).
        The functions are curried to allow for passing parameters:
        - executeADCImm(self) -> return function execute.
        """
        self._optimize_decode_lut()

        self._clock_cycles_total = 0
        self._clock_cycles = 0
        self._hz = 20
        self._current_instruction = 0x00
        self._instructions_total = 0

        self._registers = {
            "A": 0,
            "X": 0,
            "Y": 0,
            "S": 0
        }
        """
        A, X, Y and S are 8-Bit.
        """

        self ._pc = 0 # PC is 16-Bit

        self._flags = {
            "carry": False,
            "zero": False,
            "interrupt disable": False,
            "decimal mode": False,
            "break command": False,
            "overflow": False,
            "negative": False
        }
        """
        carry, 
        zero, 
        interrupt disable, 
        decimal mode, 
        break command, 
        overflow, 
        negative
        """

    def __str__(self):
        return "Registers: "+ str(self._registers) + "\n" + str(self._flags) + "\n"

    @property
    def memory(self): 
        return self._memory

    @property
    def clock_cycles_total(self):
        return self._clock_cycles_total
    
    @property
    def clock_cycles(self):
        return self._clock_cycles
    
    @clock_cycles.setter
    def clock_cycles(self, val):
        self._clock_cycles = val

    @property
    def instructions_total(self):
        return self._instructions_total

    @property
    def pc(self): 
        return self._pc

    @pc.setter
    def pc(self, val):
        if type(val) != int: raise ValueError("pc must be int")
        if val < 0 or val > 65535: raise ValueError("pc must be 16-Bit")
        self._pc = val
        return self
    
    def fetch(self, offset=0):
        return self._memory.get_byte((self.pc + offset) &0xFFFF)
    
    def fetch_two(self, offset=0):
        return (self._memory.get_byte((self.pc + offset + 1) &0xFFFF) << 8) | self._memory.get_byte((self.pc + offset) &0xFFFF)

    def run(self):
        '''
        run reset() before running to load the reset vector into PC
        '''
        while True:
            self._clock_cycles = 0
            cycle_start_time = time.perf_counter()

            self._current_instruction = self.fetch()
            self._decodeFunctionLookupTable[self._current_instruction]()

            cycle_end_time = time.perf_counter()
            wait_until = cycle_start_time + self._clock_cycles / self._hz
            self._clock_cycles_total += self._clock_cycles
            self._instructions_total += 1
            while time.perf_counter() < wait_until: pass
    
    def reset(self):
        '''
        Performs the 6502 reset procedure:
        - loads resetVector from 0xFFFC - 0xFFFD
        - sets PC to the value (address) contained in reset vector
        - sets SP to 0xFD
        this takes 8 clock cycles
        '''
        resetVectorLoByte = self._memory.get_byte(0xFFFC)
        resetVectorHiByte = self._memory.get_byte(0xFFFD)
        reset_vector = resetVectorHiByte << 8 | resetVectorLoByte
        self.pc = reset_vector
        self.set_register("S", 0xFD)
        self._clock_cycles_total += 8
    
    def get_register(self, reg):
        '''
        X, Y, A, S
        '''
        assert(reg in ("X", "Y", "A", "S"))
        return self._registers[reg]
    
    def set_register(self, reg, val):
        '''
        X, Y, A, S
        '''
        assert(type(val) == int)
        assert(reg in ("X", "Y", "A", "S"))
        assert(val >= 0 and val < 256)
        self._registers[reg] = val

    def get_flag(self, flag):
        '''
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        '''
        return self._flags[flag]
    
    def set_flag(self, flag, val):
        '''
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        '''
        assert(type(val) == bool)
        self._flags[flag] = val
    
    def set_flags_from_byte(self, byte):
        '''
        takes in an integer which represents a byte and interprets it as the flag register. Used for stack pulls.
        b7 = Negative
        b6 = Overflow
        b5 ignored
        b4 ignored
        b3 = Decimal
        b2 = Interrupt
        b1 = Zero
        b0 = Carry
        '''
        self.set_flag("negative", True if byte & 0b10000000 else False)
        self.set_flag("overflow", True if byte & 0b01000000 else False)
        self.set_flag("decimal mode", True if byte & 0b00001000 else False)
        self.set_flag("interrupt disable", True if byte & 0b00000100 else False)
        self.set_flag("zero", True if byte & 0b00000010 else False)
        self.set_flag("carry", True if byte & 0b00000001 else False)
    
    def make_byte_from_flags(self):
        '''
        returns an integer that represents a byte based on the current flags. Used for stack pushes.
        b7 = Negative
        b6 = Overflow
        b5 = 1
        b4 = 1
        b3 = Decimal
        b2 = Interrupt
        b1 = Zero
        b0 = Carry
        '''
        byte = 0
        byte = byte | (0b10000000 if self.get_flag("negative") else 0)
        byte = byte | (0b01000000 if self.get_flag("overflow") else 0)
        byte = byte | (0b00001000 if self.get_flag("decimal mode") else 0)
        byte = byte | (0b00000100 if self.get_flag("interrupt disable") else 0)
        byte = byte | (0b00000010 if self.get_flag("zero") else 0)
        byte = byte | (0b00000001 if self.get_flag("carry") else 0)
        return byte
    
    def reset_flags(self):
        """
        sets all flags to False
        """
        for flagKey in self._flags.keys():
            self._flags[flagKey] = False
    
    def _optimize_decode_lut(self):
        def unimplemented(i):
            def execute(): raise Exception("unimplemented instruction: " + hex(i))
            return execute

        lutArr = [unimplemented(i) for i in range(256)]

        for i, func in self._decodeFunctionLookupTable.items():
            lutArr[i] = func

        self._decodeFunctionLookupTable = lutArr 


if __name__ == "__main__":
    memory = Memory()
    memory.set_bytes(0x1000, [0xAA, 0xAA, 0x94, 12, 0x8D, 0x00, 0x20, 0x9D, 0x11, 0x22, 0x81, 0x23, 0x91, 0x25])
    cpu = CPU(memory)
    cpu.reset()
    cpu.set_register("A", 12)
    cpu.run()