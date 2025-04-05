import numpy as np
import time

from memory import Memory
from execution import *

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

            # TXS
            0x9A: executeTXS(self),

            # JMP
            0x4C: executeJumpDirect(self),
            0x6C: executeJumpIndirect(self, memory),

            # ADC TODO BCD
            0x69: executeADCImm(self),
            0x65: executeADCZeroPage(self, memory),
            0x75: executeADCZeroPageX(self, memory),
            0x6D: executeADCAbsolute(self, memory),
            0x7D: executeADCAbsoluteIndexed(self, memory, "X"),
            0x79: executeADCAbsoluteIndexed(self, memory, "Y"),
            0x61: executeADCIndirectIndexed(self, memory, "X"),
            0x71: executeADCIndirectIndexed(self, memory, "Y"),

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

        self._clockCycle = np.uint64(0)
        self._clockCyclesThisCycle = np.uint16(0)
        self._clockHz = np.uint64(1)
        self._instructionCycle = np.uint64(0)

        self._registers = {
            "A": np.uint8(0),
            "X": np.uint8(0),
            "Y": np.uint8(0),
            "PC": np.uint16(0),
            "SP": np.uint8(0)
        }
        """
        A, X, Y and SP are 8-Bit.
        PC is 16-Bit.
        """

        self._flags = {
            "carry": np.bool(False),
            "zero": np.bool(False),
            "interrupt disable": np.bool(False),
            "decimal mode": np.bool(False),
            "break command": np.bool(False),
            "overflow": np.bool(False),
            "negative": np.bool(False)
        }
        """
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        """

        self.currentInstruction = np.uint8(0x00)

    def __str__(self):
        return "Registers: "+ str(self._registers) + "-\n" + str(self._flags) + "-\n"

    def run(self):
        '''
        run reset() before running to load the reset vector into PC
        '''

        while True:
            cycleBeginTime = time.time()

            self.fetchInstruction()
            self._decodeFunctionLookupTable[self.currentInstruction]()

            cycleEndTime = time.time()
            timeToSleep = self._clockCyclesThisCycle / self._clockHz - (cycleEndTime - cycleBeginTime)
            self._clockCyclesThisCycle = 0
            time.sleep(timeToSleep)
    
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
        pc = self.getRegister("PC")
        self.currentInstruction = self._memory.getByte(pc)
        return self
    
    def incrementPC(self):
        self.setRegister("PC", self.getRegister("PC") + 1)
        return self

    def reset(self):
        '''
        Performs the 6502 reset procedure:
        - loads resetVector from 0xFFFC - 0xFFFD
        - sets PC to the value (address) contained in reset vector
        - this takes 8 clock cycles
        '''
        resetVectorLoByte = self._memory.getByte(0xFFFC)
        resetVectorHiByte = self._memory.getByte(0xFFFD)
        resetVector = np.uint16(resetVectorHiByte) << 8 | np.uint16(resetVectorLoByte)
        self.setRegister("PC", resetVector)
        self._clockCycle += 8
    
    def addClockCyclesThisCycle(self, n):
        '''
        clock cycles are necessary to determine the correct amount of time an instruction takes to execute
        '''
        self._clockCyclesThisCycle += n

    def getRegister(self, reg):
        '''
        X, Y, A, PC, SP
        '''
        return self._registers[reg]
    
    def setRegister(self, reg, val):
        '''
        X, Y, A, PC, SP
        '''
        self._registers[reg] = val
    
    def getFlag(self, flag):
        '''
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        '''
        return self._flags[flag]
    
    def setFlag(self, flag, val):
        '''
        carry, zero, interrupt disable, decimal mode, break command, overflow, negative
        '''
        assert(type(val) == bool or type(val) == np.bool)
        self._flags[flag] = np.bool(val)
    
    def resetFlags(self):
        """
        sets all flags to False
        """
        for flagKey in self._flags.keys():
            self._flags[flagKey] = np.bool(False)

    def resetAllRegisters(self):
        """
        resets registers (including PC) and flags
        """
        for registerKey in self._registers.keys():
            if registerKey == "PC":
                self._registers[registerKey] = np.uint16(0)
            else:
                self._registers[registerKey] = np.uint8(0)
        for flagKey in self._flags.keys():
            self._flags[flagKey] = np.bool(False)