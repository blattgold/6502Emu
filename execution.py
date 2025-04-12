def Load2ByteAddress(cpu):
    cpu.incrementPC().fetchInstruction()
    addrLo = cpu.currentInstruction
    cpu.incrementPC().fetchInstruction()
    addrHi = cpu.currentInstruction
    return (addrHi << 8) | addrLo

# NOP
def executeNOP(cpu): return lambda: cpu.incrementPC().addClockCyclesThisCycle(2)

# Transfer
def transfer(origin, destination, cpu):
    reg = cpu.getRegister(origin)
    cpu.setRegister(destination, reg)
    cpu.incrementPC().addClockCyclesThisCycle(2)
    setDecIncFlags(reg, cpu)

def executeTAX(cpu): return lambda: transfer("A",  "X",  cpu)
def executeTAY(cpu): return lambda: transfer("A",  "Y",  cpu)
def executeTSX(cpu): return lambda: transfer("SP", "X",  cpu)
def executeTXA(cpu): return lambda: transfer("X",  "A",  cpu)
def executeTYA(cpu): return lambda: transfer("Y",  "A",  cpu)
def executeTXS(cpu):
    def execute():
        x = cpu.getRegister("X")
        cpu.setRegister("SP", x)
        cpu.incrementPC().addClockCyclesThisCycle(2)
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
        cpu.incrementPC().addClockCyclesThisCycle(2)

def executeBCC(cpu): return lambda: executeBranch(not cpu.getFlag("carry"),    cpu)
def executeBCS(cpu): return lambda:     executeBranch(cpu.getFlag("carry"),    cpu)
def executeBEQ(cpu): return lambda:     executeBranch(cpu.getFlag("zero"),     cpu)
def executeBMI(cpu): return lambda:     executeBranch(cpu.getFlag("negative"), cpu)
def executeBNE(cpu): return lambda: executeBranch(not cpu.getFlag("zero"),     cpu)
def executeBPL(cpu): return lambda: executeBranch(not cpu.getFlag("negative"), cpu)
def executeBVC(cpu): return lambda: executeBranch(not cpu.getFlag("overflow"), cpu)
def executeBVS(cpu): return lambda:     executeBranch(cpu.getFlag("overflow"), cpu)

# JMP
def executeJumpDirect(cpu): return lambda: cpu.setPC(Load2ByteAddress(cpu)).addClockCyclesThisCycle(3)
def executeJumpIndirect(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        memValueAddrLo = memory.getByte(addr)
        memValueAddrHi = memory.getByte(addr + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo
        cpu.setPC(memValueAddr).addClockCyclesThisCycle(5)
    return execute

# CPX and CPY TODO tests
def setCPRegFlags(cpu, regOperand, operand):
    result = (regOperand - operand) & 0xFF
    cpu.setFlag("carry", regOperand >= operand)
    cpu.setFlag("zero", result == 0)
    cpu.setFlag("negative", (result & 0b10000000) != 0)

def executeCPRegImmediate(cpu, reg):
    def execute():
        cpu.incrementPC()
        operand = cpu.currentInstruction
        regOperand = cpu.getRegister(reg)

        setCPRegFlags(cpu, regOperand, operand)

        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeCPRegZeroPage(cpu, memory, reg):
    def execute():
        cpu.incrementPC()
        operand = memory.getByte(cpu.currentInstruction)
        regOperand = cpu.getRegister(reg)

        setCPRegFlags(cpu, regOperand, operand)

        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeCPRegAbsolute(cpu, memory, reg):
    def execute():
        operand = Load2ByteAddress(cpu)
        regOperand = cpu.getRegister(reg)

        setCPRegFlags(cpu, regOperand, operand)

        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

# STA TODO tests
def executeSTAZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().cpu.fetchInstruction()
        addr = cpu.currentInstruction
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeSTAZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().cpu.fetchInstruction()
        addr = (cpu.currentInstruction + cpu.getRegister("X")) &0xFF
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeSTAAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeSTAAbsoluteIndexed(cpu, memory, register):
    def execute():
        addr = Load2ByteAddress(cpu) + cpu.getRegister(register)
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC().addClockCyclesThisCycle(5)
    return execute

def executeSTAIndirectIndexed(cpu, memory, register):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))
        memValueAddrHi = memory.getByte(cpu.currentInstruction + cpu.getRegister("X") + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo

        a = cpu.getRegister("A")
        memory.setByte(memValueAddr, a)

        cpu.incrementPC().addClockCyclesThisCycle(6)
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction)
        memValueAddrHi = memory.getByte(cpu.currentInstruction + 1)
        memValueAddr = (memValueAddrHi << 8) | memValueAddrLo
        memValueAddrOffsetY = memValueAddr + cpu.getRegister("Y")

        a = cpu.getRegister("A")
        memory.setByte(memValueAddr, a)

        cpu.incrementPC().addClockCyclesThisCycle(6)
    return executeX if register == "X" else executeY

# STX
def executeSTXZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        result8 = memory.getByte(addr)
        cpu.setRegister("X", result8)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeSTXZeroPageY(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction + cpu.getRegister("Y")
        result8 = memory.getByte(addr)
        cpu.setRegister("X", result8)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeSTXAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        result8 = memory.getByte(addr)
        cpu.setRegister("X", result8)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

# STY
def executeSTYZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        result8 = memory.getByte(addr)
        cpu.setRegister("Y", result8)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeSTYZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction + cpu.getRegister("X")
        result8 = memory.getByte(addr)
        cpu.setRegister("Y", result8)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeSTYAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        result8 = memory.getByte(addr)
        cpu.setRegister("Y", result8)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

# increment TODO tests
def setDecIncFlags(val, cpu):
    cpu.setFlag("zero", val == 0)
    cpu.setFlag("negative", val > 127)

def executeINCZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        result8 = (memory.getByte(addr) + 1) & 0xFF
        memory.setByte(addr, result8)

        setDecIncFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return execute

def executeINCZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        result8 = (memory.getByte(addr) + 1) & 0xFF
        memory.setByte(addr, result8)

        setDecIncFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(6)
    return execute

def executeINCAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        result8 = (memory.getByte(addr) + 1) & 0xFF
        memory.setByte(addr, result8)

        setDecIncFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(6)
    return execute

def executeINCAbsoluteX(cpu, memory):
    def execute():
        addr = (Load2ByteAddress(cpu) + cpu.getRegister("X")) & 0xFFFF
        result8 = (memory.getByte(addr) + 1) & 0xFF
        memory.setByte(addr, result8)

        setDecIncFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(7)
    return execute

# decrement TODO tests
def executeDEX(cpu):
    def execute():
        x = (cpu.getRegister("X") - 1) & 0xFF
        cpu.setRegister("X", x)
        setDecIncFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeDEY(cpu):
    def execute():
        y = (cpu.getRegister("Y") - 1) & 0xFF
        cpu.setRegister("Y", y)
        setDecIncFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

# ADC TODO refactor
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
        cpu.incrementPC().addClockCyclesThisCycle(2)
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
        cpu.incrementPC().addClockCyclesThisCycle(3)
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
        cpu.incrementPC().addClockCyclesThisCycle(4)
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
        cpu.incrementPC().addClockCyclesThisCycle(4)
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
        cpu.incrementPC().addClockCyclesThisCycle(4)
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

        cpu.incrementPC().addClockCyclesThisCycle(6)
    
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
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY

# TODO SBC tests Refactor
def executeSBCImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = cpu.currentInstruction
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeSBCZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = memory.getByte(cpu.currentInstruction)
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeSBCZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeSBCAbsolute(cpu, memory):
    def execute():
        operand = memory.getByte(Load2ByteAddress(cpu))
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeSBCAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = addr + cpu.getRegister(offsetRegister)

        operand = memory.getByte(addrOffset)
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)

        # add one cycle if indexing resulted in page flip
        if addrOffset // 256 != addr // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeSBCIndirectIndexed(cpu, memory, offsetRegister):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))
        memValueAddrHi = memory.getByte(cpu.currentInstruction + cpu.getRegister("X") + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo

        operand = memory.getByte(memValueAddr)
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)

        cpu.incrementPC().addClockCyclesThisCycle(6)
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction)
        memValueAddrHi = memory.getByte(cpu.currentInstruction + 1)
        memValueAddr = (memValueAddrHi << 8) | memValueAddrLo
        memValueAddrOffsetY = memValueAddr + cpu.getRegister("Y")

        operand = memory.getByte(memValueAddrOffsetY)
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)

        # add one cycle if indexing resulted in page flip
        if memValueAddr // 256 != memValueAddrOffsetY // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY

# LDA TODO refactor
def LDSetFlags(result, cpu):
    cpu.setFlag("zero",     result ==  0)
    cpu.setFlag("negative", result > 127)

def executeLDAImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()

        newAValue = cpu.currentInstruction
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeLDAZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()

        newAValue = memory.getByte(cpu.currentInstruction)
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeLDAZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        memValue = memory.getByte(cpu.currentInstruction + cpu.getRegister("X"))

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDAAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        memValue = memory.getByte(addr)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDAAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffsetX = addr + cpu.getRegister(offsetRegister)
        memValue = memory.getByte(addrOffsetX)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        if addrOffsetX // 256 != addr // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
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

        cpu.incrementPC().addClockCyclesThisCycle(6)
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        memValueAddrLo = memory.getByte(cpu.currentInstruction)
        memValueAddrHi = memory.getByte(cpu.currentInstruction + 1)
        memValueAddr = memValueAddrHi << 8 | memValueAddrLo
        memValueAddrOffsetY = memValueAddr + cpu.getRegister("Y")
        memValue = memory.getByte(memValueAddrOffsetY)

        newAValue = memValue
        cpu.setRegister("A", newAValue)

        LDSetFlags(newAValue, cpu)

        if memValueAddr // 256 != memValueAddrOffsetY // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY

# LDX
def executeLDXImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        newXValue = cpu.currentInstruction
        cpu.setRegister("X", newXValue)
        LDSetFlags(newXValue, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeLDXZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        x = memory.getByte(addr)
        cpu.setRegister("X", x)
        LDSetFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeLDXZeroPageY(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        x = memory.getByte(addr + cpu.getRegister("Y"))
        cpu.setRegister("X", x)
        LDSetFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDXAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        x = memory.getByte(addr)
        cpu.setRegister("X", x)
        LDSetFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDXAbsoluteY(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = addr + cpu.getRegister("Y")
        x = memory.getByte(addrOffset)
        cpu.setRegister("X", x)
        LDSetFlags(x, cpu)
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

# LDY
def executeLDYImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        y = cpu.currentInstruction
        cpu.setRegister("Y", y)
        LDSetFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeLDYZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        y = memory.getByte(addr)
        cpu.setRegister("Y", y)
        LDSetFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeLDYZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        y = memory.getByte(addr + cpu.getRegister("X"))
        cpu.setRegister("Y", y)
        LDSetFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDYAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        y = memory.getByte(addr)
        cpu.setRegister("Y", y)
        LDSetFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDYAbsoluteX(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = addr + cpu.getRegister("X")
        y = memory.getByte(addrOffset)
        cpu.setRegister("Y", y)
        LDSetFlags(y, cpu)
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute