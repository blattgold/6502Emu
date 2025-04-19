import time

from memory import Memory
from cpu_state import CPUState
from instruction_handling import transfer as trans

class CPU:
    '''
    CPU class :3
    '''
    def __init__(self, memory, test=False):
        self._test = test
        self._memory = memory
        self._state = CPUState(empty=False)

        self._decodeFunctionLookupTable = {
            # Transfer
            0xAA: trans.InstructionTransfer(self._state, memory, "A", "X"), # TAX
            0xA8: trans.InstructionTransfer(self._state, memory, "A", "Y"), # TAY
            0xBA: trans.InstructionTransfer(self._state, memory, "S", "X"), # TSX
            0x8A: trans.InstructionTransfer(self._state, memory, "X", "A"), # TXA
            0x9A: trans.InstructionTransfer(self._state, memory, "X", "S"), # TXS
            0x98: trans.InstructionTransfer(self._state, memory, "Y", "A"), # TYA
            # Store
            0x86: trans.InstructionStoreZeroPage(self._state, memory, "X"), # STX (ZP)
            0x84: trans.InstructionStoreZeroPage(self._state, memory, "Y"), # STY (ZP)
            0x85: trans.InstructionStoreZeroPage(self._state, memory, "A"), # STA (ZP)
            0x96: trans.InstructionStoreZeroPageIndexed(self._state, memory, "X", "Y"), # STX,Y (ZP)
            0x94: trans.InstructionStoreZeroPageIndexed(self._state, memory, "Y", "X"), # STY,X (ZP)
            0x95: trans.InstructionStoreZeroPageIndexed(self._state, memory, "A", "X"), # STA,X (ZP)
            0x8E: trans.InstructionStoreAbsolute(self._state, memory, "X"), # STX (Abs)
            0x8C: trans.InstructionStoreAbsolute(self._state, memory, "Y"), # STY (Abs)
            0x8D: trans.InstructionStoreAbsolute(self._state, memory, "A"), # STA (Abs)
            0x9D: trans.InstructionStoreAbsoluteIndexed(self._state, memory, "A", "X"), # STA,X (Abs)
            0x99: trans.InstructionStoreAbsoluteIndexed(self._state, memory, "A", "Y"), # STA,Y (Abs)
            0x81: trans.InstructionStoreIndirectIndexed(self._state, memory, "A", "X"), # STA,X (Ind)
            0x91: trans.InstructionStoreIndirectIndexed(self._state, memory, "A", "Y"), # STA,Y (Ind)
        }
        """
        Maps opcodes to execution functions.
        Parameters are components needed to execute the function.
        Parameters specify a register for some instructions to reduce redundant code.
        - ADCImm requires the cpu registers, which is why it gets a reference to self (the cpu).
        - ADCZPage additionally gets a reference to the memory because it operates on it.
        - LDAAbsoluteIndexed additionally takes a String of the Register to index with (X or Y).
        The functions are curried to allow for passing parameters:
        - executeADCImm(self) -> return function execute.
        """
        self._optimize_decode_lut()


    def __str__(self):
        return self.state

    @property
    def memory(self): 
        return self._memory

    @property
    def state(self):
        return self._state
    
    def reset_state(self):
        self._state.reset_state()
    
    def fetch(self, offset=0):
        return self._memory.get_byte((self.state.get_by_id("pc") + offset) &0xFFFF)
    
    def fetch_two(self, offset=0):
        return (self._memory.get_byte((self.state.get_by_id("pc") + offset + 1) &0xFFFF) << 8) | self._memory.get_byte((self.state.get_by_id("pc") + offset) &0xFFFF)

    def run(self) -> CPUState:
        '''
        run reset() before running to load the reset vector into PC
        if self._test == True then it will only run one instruction per call
        '''
        while True:
            cycle_start_time = time.perf_counter()

            self.state.set_by_id("clock_cycles", 0)
            self._current_instruction = self.fetch()
            self._decodeFunctionLookupTable[self._current_instruction]()
            self.state.set_by_id("clock_cycles_total", self.state.get_by_id("clock_cycles_total") + self.state.get_by_id("clock_cycles"))
            self.state.set_by_id("instructions_total", self.state.get_by_id("instructions_total") + 1)

            if self._test: break

            cycle_end_time = time.perf_counter()
            wait_until = cycle_start_time + self.state.get_by_id("clock_cycles") / self.state.get_by_id("hz")
            while time.perf_counter() < wait_until: pass
        
        return self._state.get_state_copy()
    
    def reset(self):
        '''
        Performs the 6502 reset procedure:
        - loads resetVector from 0xFFFC - 0xFFFD
        - sets PC to the value (address) contained in reset vector
        - sets S to 0xFD
        this takes 8 clock cycles
        '''
        resetVectorLoByte = self._memory.get_byte(0xFFFC)
        resetVectorHiByte = self._memory.get_byte(0xFFFD)
        reset_vector = resetVectorHiByte << 8 | resetVectorLoByte
        self.state.set_by_id("pc", reset_vector)
        self.state.set_by_id("S", 0xFD)
        self.state.set_by_id("clock_cycles_total", self.state.get_by_id("clock_cycles_total") + 8)
    
    def set_flags_from_byte(self, byte):
        '''
        takes in an integer which represents a byte and interprets it as the flag register. Used for stack pulls.
        b7 = N
        b6 = V
        b5 ignored
        b4 ignored
        b3 = D
        b2 = I
        b1 = Z
        b0 = C
        '''
        self.set_flag("N", True if byte & 0b10000000 else False)
        self.set_flag("V", True if byte & 0b01000000 else False)
        self.set_flag("D", True if byte & 0b00001000 else False)
        self.set_flag("I", True if byte & 0b00000100 else False)
        self.set_flag("Z", True if byte & 0b00000010 else False)
        self.set_flag("C", True if byte & 0b00000001 else False)
    
    def make_byte_from_flags(self):
        '''
        returns an integer that represents a byte based on the current flags. Used for stack pushes.
        b7 = N
        b6 = V
        b5 = 1
        b4 = 1
        b3 = D
        b2 = I
        b1 = Z
        b0 = C
        '''
        byte = 0
        byte = byte | (0b10000000 if self.get_flag("N") else 0)
        byte = byte | (0b01000000 if self.get_flag("V") else 0)
        byte = byte | (0b00001000 if self.get_flag("D") else 0)
        byte = byte | (0b00000100 if self.get_flag("I") else 0)
        byte = byte | (0b00000010 if self.get_flag("Z") else 0)
        byte = byte | (0b00000001 if self.get_flag("C") else 0)
        return byte
    
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
    cpu.state.set_by_id("A", 12)
    cpu.run()