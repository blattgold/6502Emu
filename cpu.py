import time

from memory import Memory
from execution import *

def toGhz(hz: int): return hz * 1000000000
def toMhz(hz: int): return hz * 1000000
def toKhz(hz: int): return hz * 1000

class CPU:
    '''
    CPU class :3
    '''
    def __init__(self, memory):
        self._memory = memory

        self._decodeFunctionLookupTable = {
            # NOP
            0xEA: executeNOP(self),

            # CLD
            0xD8: executeCLD(self),

            # Transfer
            0xAA: executeTAX(self),
            0xA8: executeTAY(self),
            0xBA: executeTSX(self),
            0x8A: executeTXA(self),
            0x9A: executeTXS(self),
            0x98: executeTYA(self),

            # STACK
            0x28: executeStackPull(self, memory, "Flags"),
            0x68: executeStackPull(self, memory, "A"),

            # BRANCH
            0x90: executeBCC(self),
            0xB0: executeBCS(self),
            0xF0: executeBEQ(self),
            0x30: executeBMI(self),
            0xD0: executeBNE(self),
            0x10: executeBPL(self),
            0x50: executeBVC(self),
            0x70: executeBVS(self),

            # JMP
            0x4C: executeJumpDirect(self),
            0x6C: executeJumpIndirect(self, memory),

            # CPX CPY
            0xE0: executeCPRegImmediate(self, "X"),
            0xC0: executeCPRegImmediate(self, "Y"),
            0xE4: executeCPRegZeroPage(self, memory, "X"),
            0xC4: executeCPRegZeroPage(self, memory, "Y"),
            0xEC: executeCPRegAbsolute(self, memory, "X"),
            0xCC: executeCPRegAbsolute(self, memory, "Y"),

            #CMP
            0xC9: executeCPRegImmediate(self, "A"),
            0xC5: executeCPRegZeroPage(self, memory, "A"),
            0xD5: executeCPRegZeroPageX(self, memory, "A"),
            0xCD: executeCPRegZeroPage(self, memory, "A"),

            # STA
            0x85: executeSTAZeroPage(self, memory),
            0x95: executeSTAZeroPageX(self, memory),
            0x8D: executeSTAAbsolute(self, memory),
            0x9D: executeSTAAbsoluteIndexed(self, memory, "X"),
            0x99: executeSTAAbsoluteIndexed(self, memory, "Y"),
            0x81: executeSTAIndirectIndexed(self, memory, "X"),
            0x91: executeSTAIndirectIndexed(self, memory, "Y"),

            # STX
            0x86: executeSTXZeroPage(self, memory),
            0x96: executeSTXZeroPageY(self, memory),
            0x8E: executeSTXAbsolute(self, memory),

            # STY
            0x84: executeSTYZeroPage(self, memory),
            0x94: executeSTYZeroPageX(self, memory),
            0x8C: executeSTYAbsolute(self, memory),

            # Increment
            0xE6: executeINCZeroPage(self, memory),
            0xF6: executeINCZeroPageX(self, memory),
            0xEE: executeINCAbsolute(self, memory),
            0xFE: executeINCAbsoluteX(self, memory),

            # Decrement
            0xCA: executeDEX(self),
            0x88: executeDEY(self),

            # ADC TODO BCD
            0x69: executeADCImm(self),
            0x65: executeADCZeroPage(self, memory),
            0x75: executeADCZeroPageX(self, memory),
            0x6D: executeADCAbsolute(self, memory),
            0x7D: executeADCAbsoluteIndexed(self, memory, "X"),
            0x79: executeADCAbsoluteIndexed(self, memory, "Y"),
            0x61: executeADCIndirectIndexed(self, memory, "X"),
            0x71: executeADCIndirectIndexed(self, memory, "Y"),

            # SBC TODO BCD TESTS
            0xE9: executeSBCImm(self),
            0xE5: executeSBCZeroPage(self, memory),
            0xF5: executeSBCZeroPageX(self, memory),
            0xED: executeSBCAbsolute(self, memory),
            0xFD: executeSBCAbsoluteIndexed(self, memory, "X"),
            0xF9: executeSBCAbsoluteIndexed(self, memory, "Y"),
            0xE1: executeSBCIndirectIndexed(self, memory, "X"),
            0xF1: executeSBCIndirectIndexed(self, memory, "Y"),

            # LDA
            0xA9: executeLDAImm(self),
            0xA5: executeLDAZeroPage(self, memory),
            0xB5: executeLDAZeroPageX(self, memory),
            0xAD: executeLDAAbsolute(self, memory),
            0xBD: executeLDAAbsoluteIndexed(self, memory, "X"),
            0xB9: executeLDAAbsoluteIndexed(self, memory, "Y"),
            0xA1: executeLDAIndirectIndexed(self, memory, "X"),
            0xB1: executeLDAIndirectIndexed(self, memory, "Y"),

            # LDX
            0xA2: executeLDXImm(self),
            0xA6: executeLDXZeroPage(self, memory),
            0xB6: executeLDXZeroPageY(self, memory),
            0xAE: executeLDXAbsolute(self, memory),
            0xBE: executeLDXAbsoluteY(self, memory),

            #LDY
            0xA0: executeLDYImm(self),
            0xA4: executeLDYZeroPage(self, memory),
            0xB4: executeLDYZeroPageX(self, memory),
            0xAC: executeLDYAbsolute(self, memory),
            0xBC: executeLDYAbsoluteX(self, memory),

            #ORA
            0x09: executeORAIMM(self),
            0x05: executeORAZeroPage(self, memory),
            0x15: executeORAZeroPageX(self, memory),
            0x0D: executeORAAbsolute(self, memory),
            0x1D: executeORAAbsoluteIndexed(self, memory, "X"),
            0x19: executeORAAbsoluteIndexed(self, memory, "Y"),
            0x01: executeORAIndirectIndexed(self, memory, "X"),
            0x11: executeORAIndirectIndexed(self, memory, "Y"),
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

        self._clockCycle = 0
        self._clockCyclesThisCycle = 0
        self._clockHz = toKhz(10)
        self._instructionCycle = 0

        self._registers = {
            "A": 0,
            "X": 0,
            "Y": 0,
            "PC": 0,
            "SP": 0
        }
        """
        A, X, Y and SP are 8-Bit.
        PC is 16-Bit.
        """

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
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        """

        self.currentInstruction = 0x00

    def __str__(self):
        return "Registers: "+ str(self._registers) + "-\n" + str(self._flags) + "-\n"

    def run(self):
        '''
        run reset() before running to load the reset vector into PC
        '''
        self._optimizeDecodeLut()

        while True:
            cycleBeginTime = time.perf_counter()

            self.fetchInstruction()
            print("op-code: " + hex(self.currentInstruction))
            print("next2: " + hex(self._memory.getByte(self.getPC() + 1)) + hex(self._memory.getByte(self.getPC() + 2)))
            print(self)

            self._decodeFunctionLookupTable[self.currentInstruction]()

            cycleEndTime = time.perf_counter()
            waitUntil = cycleBeginTime + self._clockCyclesThisCycle / self._clockHz
            while time.perf_counter() < waitUntil: pass

            # debug shit
            timeTakenInstructionCycle = cycleEndTime - cycleBeginTime
            timeTakenInstructionCycleNS = timeTakenInstructionCycle * 1000000
            timeToWaitInstructionCycleNS = (waitUntil - cycleBeginTime) * 1000000
            timeClockCycleNS = timeTakenInstructionCycleNS / self._clockCyclesThisCycle
            print("time spent per instruction cycle is {n:.10f}us.".format(n = timeTakenInstructionCycleNS))
            print("time to wait in busy loop is {n:.10f}us.".format(n = timeToWaitInstructionCycleNS))
            print("time per clock cycle is {n:.10f}us.\n".format(n = timeClockCycleNS))
            print(self)

            self._clockCyclesThisCycle = 0
    
    def runPerfTest(self, program):
        self._optimizeDecodeLut()
        self._memory.setBytes(0x1000, program)
        self.setPC(0x1000)
        
        times = []

        for i in range(len(program) // 3):
            cycleBeginTime = time.perf_counter()
            self.fetchInstruction()
            self._decodeFunctionLookupTable[self.currentInstruction]()
            self._clockCyclesThisCycle = 0

            timeTakenInstructionCycle = (time.perf_counter() - cycleBeginTime) * 1000000
            times.append(timeTakenInstructionCycle)
        return times
    
    def _optimizeDecodeLut(self):
        def unimplemented(i):
            def execute(): raise Exception("unimplemented instruction: " + hex(i))
            return execute

        lutArr = [unimplemented(i) for i in range(256)]

        for i, func in self._decodeFunctionLookupTable.items():
            lutArr[i] = func

        self._decodeFunctionLookupTable = lutArr

    def runSingleInstructionCycle(self):
        '''
        Run reset() before, if this is the first cycle.
        Runs a single instruction cycle
        Returns the number of clock cycles used
        '''
        self.fetchInstruction()
        self._decodeFunctionLookupTable[self.currentInstruction]()
        clockCycles = self._clockCyclesThisCycle
        self._clockCyclesThisCycle = 0
        return clockCycles
    
    def fetchInstruction(self):
        '''
        loads the next instruction into currentInstruction
        '''
        pc = self.getPC()
        self.currentInstruction = self._memory.getByte(pc)
        return self
    
    def incrementPC(self):
        self.setPC(self.getPC() + 1)
        return self

    def reset(self):
        '''
        Performs the 6502 reset procedure:
        - loads resetVector from 0xFFFC - 0xFFFD
        - sets PC to the value (address) contained in reset vector
        - sets SP to 0xFD
        this takes 8 clock cycles
        '''
        resetVectorLoByte = self._memory.getByte(0xFFFC)
        resetVectorHiByte = self._memory.getByte(0xFFFD)
        resetVector = resetVectorHiByte << 8 | resetVectorLoByte
        self.setPC(resetVector)
        self.setRegister("SP", 0xFD)
        self._clockCycle += 8
    
    def addClockCyclesThisCycle(self, n):
        '''
        clock cycles are necessary to determine the correct amount of time an instruction takes to execute
        '''
        self._clockCyclesThisCycle += n

    def getRegister(self, reg):
        '''
        X, Y, A, SP
        '''
        assert(reg in ("X", "Y", "A", "SP"))
        return self._registers[reg]
    
    def setRegister(self, reg, val):
        '''
        X, Y, A, SP
        '''
        assert(type(val) == int)
        assert(reg in ("X", "Y", "A", "SP"))
        assert(val >= 0 and val < 256)
        self._registers[reg] = val
    
    def getPC(self):
        return self._registers["PC"]

    def setPC(self, val):
        assert(type(val) == int)
        assert(val >= 0 and val < 65536)
        self._registers["PC"] = val
        return self

    
    def getFlag(self, flag):
        '''
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        '''
        return self._flags[flag]
    
    def setFlag(self, flag, val):
        '''
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        '''
        assert(type(val) == bool)
        self._flags[flag] = val
    
    def setFlagsFromByte(self, byte):
        '''
        takes in an integer which represents a byte and interprets it as the flag register
        b7 = Negative
        b6 = Overflow
        b5 ignored
        b4 ignored
        b3 = Decimal
        b2 = Interrupt
        b1 = Zero
        b0 = Carry
        '''
        self.setFlag("negative", True if byte & 0b10000000 else False)
        self.setFlag("overflow", True if byte & 0b01000000 else False)
        self.setFlag("decimal mode", True if byte & 0b00001000 else False)
        self.setFlag("interrupt disable", True if byte & 0b00000100 else False)
        self.setFlag("zero", True if byte & 0b00000010 else False)
        self.setFlag("carry", True if byte & 0b00000001 else False)
    
    def resetFlags(self):
        """
        sets all flags to False
        """
        for flagKey in self._flags.keys():
            self._flags[flagKey] = False

    def resetAllRegisters(self):
        """
        resets registers (including PC) and flags
        """
        for registerKey in self._registers.keys():
            if registerKey == "PC":
                self._registers[registerKey] = 0
            else:
                self._registers[registerKey] = 0
        for flagKey in self._flags.keys():
            self._flags[flagKey] = False


if __name__ == "__main__":
    memory = Memory()
    cpu = CPU(memory)
    cpu.reset()
    test = []
    for i in range(15000):
        test.append(0xae)
        test.append(0x10)
        test.append(0x20)
    result = cpu.runPerfTest(test)
    print(sum(result) / len(result))