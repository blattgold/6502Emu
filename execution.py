

def Load2ByteAddress(cpu):
    cpu.incrementPC().fetchInstruction()
    addrLo = cpu.currentInstruction
    cpu.incrementPC().fetchInstruction()
    addrHi = cpu.currentInstruction
    return (addrHi << 8) | addrLo

# NOP
def executeNOP(cpu):
    def execute():
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()

    return execute

# TXS
def executeTXS(cpu):
    def execute():
        cpu.setRegister("SP", cpu.getRegister("X"))
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()

    return execute

# CLD
def executeCLD(cpu):
    def execute():
        cpu.setFlag("decimal mode", False)
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()

    return execute

# BRANCH
def executeBranch(branch, cpu):
    cpu.incrementPC().fetchInstruction()

    if branch:
        pcBefore = cpu.getPC()
        offset = cpu.currentInstruction - 256 if cpu.currentInstruction > 127 else cpu.currentInstruction
        pcAfter = pcBefore + offset
        cpu.setPC(pcAfter)

        if pcBefore // 256 != pcAfter // 256:
            cpu.addClockCyclesThisCycle(4)
        else:
            cpu.addClockCyclesThisCycle(3)

    else:
        cpu.addClockCyclesThisCycle(2)
        cpu.incrementPC()

def executeBCC(cpu):
    return lambda: executeBranch(not cpu.getFlag("carry"), cpu)

def executeBCS(cpu):
    return lambda: executeBranch(cpu.getFlag("carry"), cpu)

def executeBEQ(cpu):
    return lambda: executeBranch(cpu.getFlag("zero"), cpu)

def executeBMI(cpu):
    return lambda: executeBranch(cpu.getFlag("negative"), cpu)

def executeBNE(cpu):
    return lambda: executeBranch(not cpu.getFlag("zero"), cpu)

def executeBPL(cpu):
    return lambda: executeBranch(not cpu.getFlag("negative"), cpu)

def executeBVC(cpu):
    return lambda: executeBranch(not cpu.getFlag("overflow"), cpu)

def executeBVS(cpu):
    return lambda: executeBranch(cpu.getFlag("overflow"), cpu)

# JMP
def executeJumpDirect(cpu):
    def execute():
        addr = Load2ByteAddress(cpu)
        cpu.setPC(addr)
        cpu.addClockCyclesThisCycle(3)

    return execute

def executeJumpIndirect(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        memValueAddrLo = memory.getByte(addr)
        memValueAddrHi = memory.getByte(addr + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo
        cpu.setPC(memValueAddr)
        cpu.addClockCyclesThisCycle(5)
    return execute

# STA TODO tests
def executeSTAZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().cpu.fetchInstruction()
        addr = cpu.currentInstruction
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC()
        cpu.addClockCyclesThisCycle(3)
    return execute

def executeSTAZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().cpu.fetchInstruction()
        addr = (cpu.currentInstruction + cpu.getRegister("X")) &0xFF
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC()
        cpu.addClockCyclesThisCycle(4)
    return execute

def executeSTAAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC()
        cpu.addClockCyclesThisCycle(4)
    return execute

def executeSTAAbsoluteIndexed(cpu, memory, register):
    def execute():
        addr = Load2ByteAddress(cpu) + cpu.getRegister(register)
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC()
        cpu.addClockCyclesThisCycle(5)
    return execute

def executeSTAIndirectIndexed(cpu, memory, register):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))
        memValueAddrHi = memory.getByte(cpu.currentInstruction + cpu.getRegister("X") + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo

        a = cpu.getRegister("A")
        memory.setByte(memValueAddr, a)

        cpu.addClockCyclesThisCycle(6)
        cpu.incrementPC()
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction)
        memValueAddrHi = memory.getByte(cpu.currentInstruction + 1)
        memValueAddr = (memValueAddrHi << 8) | memValueAddrLo
        memValueAddrOffsetY = memValueAddr + cpu.getRegister("Y")

        a = cpu.getRegister("A")
        memory.setByte(memValueAddr, a)

        cpu.addClockCyclesThisCycle(6)
        cpu.incrementPC()
    return executeX if register == "X" else executeY

# decrement TODO tests
def setDecrementFlags(val, cpu):
    cpu.setFlag("zero", val == 0)
    cpu.setFlag("negative", val > 127)

def executeDEX(cpu):
    def execute():
        x = (cpu.getRegister("X") - 1) & 0xFF
        cpu.setRegister("X", x)
        setDecrementFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeDEY(cpu):
    def execute():
        y = (cpu.getRegister("Y") - 1) & 0xFF
        cpu.setRegister("Y", y)
        setDecrementFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

# ADC
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

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
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

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
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

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
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

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)
        cpu.addClockCyclesThisCycle(4)
        cpu.incrementPC()
    return execute

def executeADCAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = addr + cpu.getRegister(offsetRegister)

        operand = memory.getByte(addrOffset)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
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
        memValueAddrLo = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))
        memValueAddrHi = memory.getByte(cpu.currentInstruction + cpu.getRegister("X") + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo

        operand = memory.getByte(memValueAddr)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)

        cpu.addClockCyclesThisCycle(6)
        cpu.incrementPC()
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction)
        memValueAddrHi = memory.getByte(cpu.currentInstruction + 1)
        memValueAddr = (memValueAddrHi << 8) | memValueAddrLo
        memValueAddrOffsetY = memValueAddr + cpu.getRegister("Y")

        operand = memory.getByte(memValueAddrOffsetY)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)

        # add one cycle if indexing resulted in page flip
        if memValueAddr // 256 != memValueAddrOffsetY // 256: cpu.addClockCyclesThisCycle(1)
        cpu.addClockCyclesThisCycle(5)
        cpu.incrementPC()
    return executeX if offsetRegister == "X" else executeY

# LDA TODO refactor
def LDSetFlags(result, cpu):
    if result == 0: cpu.setFlag("zero", True)
    else: cpu.setFlag("zero", False)
    if result & 0b10000000: cpu.setFlag("negative", True)
    else: cpu.setFlag("negative", False)

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
        addrOffsetX = addr + cpu.getRegister(offsetRegister)
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
        memValueAddrLo = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))
        memValueAddrHi = memory.getByte(cpu.currentInstruction + cpu.getRegister("X") + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo
        memValue = memory.getByte(memValueAddr)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.addClockCyclesThisCycle(6)
        cpu.incrementPC()
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction)
        memValueAddrHi = memory.getByte(cpu.currentInstruction + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo
        memValueAddrPage = memValueAddr // 256
        memValueAddrOffsetY = memValueAddr + cpu.getRegister("Y")
        memValueAddrOffsetYPage = memValueAddrOffsetY // 256
        memValue = memory.getByte(memValueAddrOffsetY)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        if memValueAddrPage != memValueAddrOffsetYPage: cpu.addClockCyclesThisCycle(1)
        cpu.addClockCyclesThisCycle(5)
        cpu.incrementPC()
    return executeX if offsetRegister == "X" else executeY

# LDX TODO refactor
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

# LDY TODO refactor
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