import numpy as np

def Load2ByteAddress(cpu):
    cpu.incrementPC().fetchInstruction()
    addrLo = np.uint16(cpu.currentInstruction)
    cpu.incrementPC().fetchInstruction()
    addrHi = np.uint16(cpu.currentInstruction)
    return (addrHi << 8) | addrLo


def executeTXS(cpu):
    def execute():
        cpu.setRegister("SP", cpu.getRegister("X"))
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()

    return execute


def executeCLD(cpu):
    def execute():
        cpu.setFlag("decimal mode", False)
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()

    return execute




def executeJumpDirect(cpu):
    def execute():
        addr = Load2ByteAddress(cpu)
        cpu.setRegister("PC", addr)
        cpu.addClockCyclesThisCycle(3)

    return execute

def executeJumpIndirect(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        memValueAddrLo = memory.getByte(addr)
        memValueAddrHi = memory.getByte(addr + 1)
        memValueAddr = ((memValueAddrHi << 8) | memValueAddrLo)
        cpu.setRegister("PC", memValueAddr)
        cpu.addClockCyclesThisCycle(5)
    return execute


def setADCFlags(cpu, result16, result8, a, operand):
    cpu.setFlag("carry", result16 > 0xFF)
    same_sign = (a & 0x80) == (operand & 0x80)
    sign_changed = (a & 0x80) != (result8 & 0x80)
    overflow = same_sign and sign_changed
    cpu.setFlag("overflow", overflow != 0)
    cpu.setFlag("zero", result8 == 0)
    cpu.setFlag("negative", result8 & 0x80 != 0)


def executeADCImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = cpu.currentInstruction
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = np.uint16(a) + np.uint16(operand) + np.uint16(carry_in)
        result8 = np.uint8(result16)
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()
    return execute

def executeADCZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = memory.getByte(cpu.currentInstruction)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = np.uint16(a) + np.uint16(operand) + np.uint16(carry_in)
        result8 = np.uint8(result16)
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)
        cpu.addClockCyclesThisCycle(3)
        cpu.incrementPC()
    return execute

def executeADCZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = np.uint16(a) + np.uint16(operand) + np.uint16(carry_in)
        result8 = np.uint8(result16)
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeADCAbsolute(cpu, memory):
    def execute():
        operand = memory.getByte(Load2ByteAddress(cpu))
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = np.uint16(a) + np.uint16(operand) + np.uint16(carry_in)
        result8 = np.uint8(result16)
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeADCAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = addr + np.uint16(cpu.getRegister(offsetRegister))

        operand = memory.getByte(addrOffset)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = np.uint16(a) + np.uint16(operand) + np.uint16(carry_in)
        result8 = np.uint8(result16)
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)

        # add one cycle if indexing resulted in page flip
        if addrOffset // 256 != addr // 256: cpu.addClockCyclesThisCycle(1)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeADCIndirectIndexed(cpu, memory, offsetRegister):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = np.uint16(memory.getByte(cpu.currentInstruction + np.uint16(cpu.getRegister("X"))))
        memValueAddrHi = np.uint16(memory.getByte(cpu.currentInstruction + np.uint16(cpu.getRegister("X") + 1)))
        memValueAddr = ((memValueAddrHi << 8) | memValueAddrLo)

        operand = memory.getByte(memValueAddr)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")
        print(hex(cpu.currentInstruction + np.uint16(cpu.getRegister("X"))))
        print(hex(memValueAddrLo), hex(memValueAddrHi), hex(memValueAddr))

        result16 = np.uint16(a) + np.uint16(operand) + np.uint16(carry_in)
        result8 = np.uint8(result16)
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)

        cpu.addClockCyclesThisCycle(6)
        cpu.incrementPC()
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = np.uint16(memory.getByte(cpu.currentInstruction))
        memValueAddrHi = np.uint16(memory.getByte(cpu.currentInstruction + 1))
        memValueAddr = (memValueAddrHi << 8) | memValueAddrLo
        memValueAddrOffsetY = memValueAddr + np.uint16(cpu.getRegister("Y"))

        operand = memory.getByte(memValueAddrOffsetY)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = np.uint16(a) + np.uint16(operand) + np.uint16(carry_in)
        result8 = np.uint8(result16)
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)

        # add one cycle if indexing resulted in page flip
        if memValueAddr // 256 != memValueAddrOffsetY // 256: cpu.addClockCyclesThisCycle(1)
        cpu.addClockCyclesThisCycle(5)
        cpu.incrementPC()
    return executeX if offsetRegister == "X" else executeY


def LDSetFlags(result, cpu):
    if result == 0: cpu.setFlag("zero", True)
    else: cpu.setFlag("zero", False)
    if result & 0b10000000: cpu.setFlag("negative", True)
    else: cpu.setFlag("negative", False)



def LoadAddressIndirectX(cpu, memory, indexReg):
    addr = LoadAddressAbsolute(cpu, memory)
    return addr

# LDA

def executeLDAImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()

        newAValue = cpu.currentInstruction
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()
    return execute

def executeLDAZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()

        newAValue = memory.getByte(cpu.currentInstruction)
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.addClockCyclesThisCycle(3)
        cpu.incrementPC()
    return execute

def executeLDAZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        memValue = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeLDAAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        memValue = memory.getByte(addr)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeLDAAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrPage = addr // 256
        addrOffsetX = addr + np.uint16(cpu.getRegister(offsetRegister))
        addrOffsetXPage = addrOffsetX // 256
        memValue = memory.getByte(addrOffsetX)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        if addrOffsetXPage != addrPage: cpu.addClockCyclesThisCycle(1)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeLDAIndirectIndexed(cpu, memory, offsetRegister):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = np.uint16(memory.getByte(cpu.currentInstruction + np.uint16(cpu.getRegister("X"))))
        memValueAddrHi = np.uint16(memory.getByte(cpu.currentInstruction + np.uint16(cpu.getRegister("X") + 1)))
        memValueAddr = ((memValueAddrHi << 8) | memValueAddrLo)
        memValue = memory.getByte(memValueAddr)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.addClockCyclesThisCycle(6)
        cpu.incrementPC()
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = np.uint16(memory.getByte(cpu.currentInstruction))
        memValueAddrHi = np.uint16(memory.getByte(cpu.currentInstruction + 1))
        memValueAddr = (memValueAddrHi << 8) | memValueAddrLo
        memValueAddrPage = memValueAddr // 256
        memValueAddrOffsetY = memValueAddr + np.uint16(cpu.getRegister("Y"))
        memValueAddrOffsetYPage = memValueAddrOffsetY // 256
        memValue = memory.getByte(memValueAddrOffsetY)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        if memValueAddrPage != memValueAddrOffsetYPage: cpu.addClockCyclesThisCycle(1)
        cpu.addClockCyclesThisCycle(5)
        cpu.incrementPC()
    return executeX if offsetRegister == "X" else executeY

# LDX

def executeLDXImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        newXValue = cpu.currentInstruction
        cpu.setRegister("X", newXValue)
        LDSetFlags(newXValue, cpu)
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()
    return execute

def executeLDXZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        memAddr = cpu.currentInstruction
        newXValue = memory.getByte(memAddr)

        cpu.setRegister("X", newXValue)
        LDSetFlags(newXValue, cpu)
        cpu.addClockCyclesThisCycle(3)
        cpu.incrementPC()
    return execute

def executeLDXZeroPageY(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        memAddr = cpu.currentInstruction
        newXValue = memory.getByte(memAddr + cpu.getRegister("Y"))

        cpu.setRegister("X", newXValue)
        LDSetFlags(newXValue, cpu)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeLDXAbsolute(cpu, memory):
    def execute():
        memAddr = Load2ByteAddress(cpu)

        newXValue = memory.getByte(memAddr)

        cpu.setRegister("X", newXValue)
        LDSetFlags(newXValue, cpu)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeLDXAbsoluteY(cpu, memory):
    def execute():
        memAddr = Load2ByteAddress(cpu)
        memAddrOffsetY = memAddr + cpu.getRegister("Y")
        newXValue = memory.getByte(memAddrOffsetY)

        cpu.setRegister("X", newXValue)
        LDSetFlags(newXValue, cpu)

        memAddrPage = memAddr // 256
        memAddrOffsetYPage = memAddrOffsetY // 256
        if memAddrPage != memAddrOffsetYPage: cpu.addClockCyclesThisCycle(1)

        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

# LDY

def executeLDYImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        newYValue = cpu.currentInstruction
        cpu.setRegister("Y", newYValue)
        LDSetFlags(newYValue, cpu)
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()
    return execute

def executeLDYZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        memAddr = cpu.currentInstruction
        newYValue = memory.getByte(memAddr)

        cpu.setRegister("Y", newYValue)
        LDSetFlags(newYValue, cpu)
        cpu.addClockCyclesThisCycle(3)
        cpu.incrementPC()
    return execute

def executeLDYZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        memAddr = cpu.currentInstruction
        newYValue = memory.getByte(memAddr + cpu.getRegister("X"))

        cpu.setRegister("Y", newYValue)
        LDSetFlags(newYValue, cpu)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeLDYAbsolute(cpu, memory):
    def execute():
        memAddr = Load2ByteAddress(cpu)

        newYValue = memory.getByte(memAddr)

        cpu.setRegister("Y", newYValue)
        LDSetFlags(newYValue, cpu)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeLDYAbsoluteX(cpu, memory):
    def execute():
        memAddr = Load2ByteAddress(cpu)
        memAddrPage = memAddr // 256
        memAddrOffsetY = memAddr + cpu.getRegister("X")
        memAddrOffsetYPage = memAddrOffsetY // 256

        newYValue = memory.getByte(memAddrOffsetY)

        cpu.setRegister("Y", newYValue)
        LDSetFlags(newYValue, cpu)
        if memAddrPage != memAddrOffsetYPage: cpu.addClockCyclesThisCycle(1)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute