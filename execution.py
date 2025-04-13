def Load2ByteAddress(cpu):
    cpu.incrementPC().fetchInstruction()
    addrLo = cpu.currentInstruction
    cpu.incrementPC().fetchInstruction()
    addrHi = cpu.currentInstruction
    return (addrHi << 8) | addrLo

def Load2ByteAddressIndexed(cpu, reg):
    '''
    loads 2 bytes, and returns a tuple. Takes index register.
    (addr, addrIndexed)
    '''
    cpu.incrementPC().fetchInstruction()
    addrLo = cpu.currentInstruction
    addrLoOffset = (addrLo + cpu.getRegister(reg)) & 0xFF
    cpu.incrementPC().fetchInstruction()
    addrHi = cpu.currentInstruction
    addrHiOffset = (addrHi + cpu.getRegister(reg)) & 0xFF
    return (addrHi << 8) | addrLo, (addrHiOffset << 8) | addrLoOffset

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
        pcAfter = (pcBefore + offset + 1) & 0xFFFF
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
        lookupAddr = cpu.currentInstruction
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        result16 = addrHi << 8 | addrLo
        cpu.setPC(result16).addClockCyclesThisCycle(5)
    return execute

def executeStackPull(cpu, memory, reg):
    '''
    reg = A or Flags
    '''
    def execute():
        sp = cpu.getRegister("SP")
        addr = 0x0100 + sp
        operand = memory.getByte(addr)

        if reg == "Flags": cpu.setFlagsFromByte(operand)
        elif reg == "A":
            cpu.setRegister("A", operand)
            setZNFlags(operand, cpu)

        spNew = (sp + 1) & 0xFF
        cpu.setRegister("SP", spNew)
        
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeStackPush(cpu, memory, reg):
    '''
    reg = A or Flags
    '''
    def execute():
        sp = cpu.getRegister("SP")
        addr = 0x0100 + sp

        if reg == "Flags": 
            flagByte = cpu.getByteFromFlags()
            memory.setByte(addr, flagByte)
        elif reg == "A":
            a = cpu.getRegister("A")
            memory.setByte(addr, a)

        spNew = (sp + 0xFF) & 0xFF
        cpu.setRegister("SP", spNew)
        
        cpu.incrementPC().addClockCyclesThisCycle(4)
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

def executeCPRegZeroPageX(cpu, memory, reg):
    def execute():
        cpu.incrementPC()
        addr = cpu.currentInstruction
        addrOffset = (addr + cpu.getRegister(reg)) & 0xFF
        operand = memory.getByte(addrOffset)
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

def executeCPRegAbsoluteIndexed(cpu, memory, reg, indexReg):
    def execute():
        operand, operandOffset = Load2ByteAddressIndexed(cpu, indexReg)
        regOperand = cpu.getRegister(reg)

        setCPRegFlags(cpu, regOperand, operandOffset)

        if operand // 256 != operandOffset // 256: cpu.addClockCyclesThisCycle(1)
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
        addr = (Load2ByteAddress(cpu) + cpu.getRegister(register)) & 0xFFFF
        a = cpu.getRegister("A")

        memory.setByte(addr, a)

        cpu.incrementPC().addClockCyclesThisCycle(5)
    return execute

def executeSTAIndirectIndexed(cpu, memory, register):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        lookupAddr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        addr = addrHi << 8 | addrLo

        a = cpu.getRegister("A")
        memory.setByte(addr, a)

        cpu.incrementPC().addClockCyclesThisCycle(6)
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        lookupAddr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        addr = (addrHi << 8) | addrLo
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF

        a = cpu.getRegister("A")
        memory.setByte(addrOffset, a)

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
        addr = (cpu.currentInstruction + cpu.getRegister("Y")) &0xFF
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
        addr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
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
        x = cpu.getRegister("X")
        xDec = (x + 0xFF) & 0xFF
        cpu.setRegister("X", xDec)
        setDecIncFlags(xDec, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeDEY(cpu):
    def execute():
        y = cpu.getRegister("Y")
        yDec = (y + 0xFF) & 0xFF
        cpu.setRegister("Y", yDec)
        setDecIncFlags(yDec, cpu)
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
        addr = cpu.currentInstruction
        addrOffset = (addr + cpu.getRegister("X")) & 0xFF
        operand = memory.getByte(addrOffset)
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
        addrOffset = (addr + cpu.getRegister(offsetRegister)) & 0xFFFF

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
        lookupAddr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        addr = addrHi << 8 | addrLo

        operand = memory.getByte(addr)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)

        cpu.incrementPC().addClockCyclesThisCycle(6)
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        lookupAddr = cpu.currentInstruction
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        addr = (addrHi << 8) | addrLo
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF

        operand = memory.getByte(addrOffset)
        carry_in = 1 if cpu.getFlag("carry") else 0
        a = cpu.getRegister("A")

        result16 = a + operand + carry_in
        result8 = result16 &0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, operand)

        # add one cycle if indexing resulted in page flip
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
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
        addr = cpu.currentInstruction
        addrOffset = (addr + cpu.getRegister("X")) & 0xFF
        operand = memory.getByte(addrOffset)
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
        addrOffset = (addr + cpu.getRegister(offsetRegister)) & 0xFFFF

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
        lookupAddr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        AddrHi = memory.getByte(lookupAddrNext)
        addr = AddrHi << 8 | addrLo

        operand = memory.getByte(addr)
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
        addr = cpu.currentInstruction
        addrLo = memory.getByte(addr)
        addrHi = memory.getByte((addr + 1) & 0xFF)
        addr = (addrHi << 8) | addrLo
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF

        operand = memory.getByte(addrOffset)
        nOperand = (~operand + 1) & 0xFF
        borrow_in = 0 if cpu.getFlag("carry") else 1
        a = cpu.getRegister("A")

        result16 = a + nOperand - borrow_in
        result8 = result16 & 0xFF
        cpu.setRegister("A", result8)

        setADCFlags(cpu, result16, result8, a, ~operand)

        # add one cycle if indexing resulted in page flip
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY

# LDA TODO refactor
def setZNFlags(result, cpu):
    cpu.setFlag("zero",     result ==  0)
    cpu.setFlag("negative", result > 127)

def executeLDAImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()

        result8 = cpu.currentInstruction
        cpu.setRegister("A", result8)

        setZNFlags(result8, cpu)

        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeLDAZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()

        result8 = memory.getByte(cpu.currentInstruction)
        cpu.setRegister("A", result8)

        setZNFlags(result8, cpu)

        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeLDAZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrOffset = (addr + cpu.getRegister("X")) & 0xFF
        operand = memory.getByte(addrOffset)
        cpu.setRegister("A", operand)
        setZNFlags(operand, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDAAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        result8 = memory.getByte(addr)
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDAAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = (addr + cpu.getRegister(offsetRegister)) & 0xFFFF
        result8 = memory.getByte(addrOffset)
        cpu.setRegister("A", result8)

        setZNFlags(result8, cpu)

        if addrOffset // 256 != addr // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDAIndirectIndexed(cpu, memory, offsetRegister):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrOffset = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFFFF
        addrOffsetNext = (addrOffset + 1) & 0xFFFF
        addrLo = memory.getByte(addroffset)
        addrHi = memory.getByte(addrOffsetNext)
        addr = addrHi << 8 | addrLo
        result8 = memory.getByte(addr)
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(6)
    
    def executeY():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrLo = memory.getByte(addr)
        addrHi = memory.getByte((addr + 1) & 0xFF)
        addr = addrHi << 8 | addrLo
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF
        result8 = memory.getByte(addrOffset)
        cpu.setRegister("A", result8)

        setZNFlags(result8, cpu)

        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY

# LDX
def executeLDXImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        newXValue = cpu.currentInstruction
        cpu.setRegister("X", newXValue)
        setZNFlags(newXValue, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeLDXZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        x = memory.getByte(addr)
        cpu.setRegister("X", x)
        setZNFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeLDXZeroPageY(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFF
        x = memory.getByte(addrOffset)
        cpu.setRegister("X", x)
        setZNFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDXAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        x = memory.getByte(addr)
        cpu.setRegister("X", x)
        setZNFlags(x, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDXAbsoluteY(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF
        x = memory.getByte(addrOffset)
        cpu.setRegister("X", x)
        setZNFlags(x, cpu)
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

# LDY
def executeLDYImm(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        y = cpu.currentInstruction
        cpu.setRegister("Y", y)
        setZNFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeLDYZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        y = memory.getByte(addr)
        cpu.setRegister("Y", y)
        setZNFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeLDYZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrOffset = (addr + cpu.getRegister("X")) & 0xFF
        y = memory.getByte(addrOffset)
        cpu.setRegister("Y", y)
        setZNFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDYAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        y = memory.getByte(addr)
        cpu.setRegister("Y", y)
        setZNFlags(y, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeLDYAbsoluteX(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = (addr + cpu.getRegister("X")) & 0xFFFF
        y = memory.getByte(addrOffset)
        cpu.setRegister("Y", y)
        setZNFlags(y, cpu)
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

# Logical
# ORA
def executeORAIMM(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = cpu.currentInstruction
        a = cpu.getRegister("A")
        result8 = a | operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeORAZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = memory.getByte(cpu.currentInstruction)
        a = cpu.getRegister("A")
        result8 = a | operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeORAZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrOffset = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a | operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeORAAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        operand = memory.getByte(addr)
        a = cpu.getRegister("A")
        result8 = a | operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeORAAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = (addr + cpu.getRegister(offsetRegister)) & 0xFFFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a | operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        if addrOffset // 256 != addr // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeORAIndirectIndexed(cpu, memory, offsetRegister):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        lookupAddr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        addr = addrHi << 8 | addrLo
        operand = memory.getByte(addr)
        a = cpu.getRegister("A")
        result8 = a | operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(6)
    def executeY():
        cpu.incrementPC().fetchInstruction()
        addrLo = memory.getByte(cpu.currentInstruction)
        addrHi = memory.getByte(cpu.currentInstruction + 1)
        addr = addrHi << 8 | addrLo
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a | operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY
# EOR
def executeEORIMM(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = cpu.currentInstruction
        a = cpu.getRegister("A")
        result8 = a ^ operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeEORZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = memory.getByte(cpu.currentInstruction)
        a = cpu.getRegister("A")
        result8 = a ^ operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeEORZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrOffset = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a ^ operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeEORAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        operand = memory.getByte(addr)
        a = cpu.getRegister("A")
        result8 = a ^ operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeEORAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = (addr + cpu.getRegister(offsetRegister)) & 0xFFFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a ^ operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        if addrOffset // 256 != addr // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeEORIndirectIndexed(cpu, memory, offsetRegister):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        lookupAddr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        addr = addrHi << 8 | addrLo
        operand = memory.getByte(addr)
        a = cpu.getRegister("A")
        result8 = a ^ operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(6)
    def executeY():
        cpu.incrementPC().fetchInstruction()
        addrLo = memory.getByte(cpu.currentInstruction)
        addrHi = memory.getByte(cpu.currentInstruction + 1)
        addr = addrHi << 8 | addrLo
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a ^ operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY
# AND
def executeANDIMM(cpu):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = cpu.currentInstruction
        a = cpu.getRegister("A")
        result8 = a & operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(2)
    return execute

def executeANDZeroPage(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        operand = memory.getByte(cpu.currentInstruction)
        a = cpu.getRegister("A")
        result8 = a & operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(3)
    return execute

def executeANDZeroPageX(cpu, memory):
    def execute():
        cpu.incrementPC().fetchInstruction()
        addr = cpu.currentInstruction
        addrOffset = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a & operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeANDAbsolute(cpu, memory):
    def execute():
        addr = Load2ByteAddress(cpu)
        operand = memory.getByte(addr)
        a = cpu.getRegister("A")
        result8 = a & operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeANDAbsoluteIndexed(cpu, memory, offsetRegister):
    def execute():
        addr = Load2ByteAddress(cpu)
        addrOffset = (addr + cpu.getRegister(offsetRegister)) & 0xFFFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a & operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        if addrOffset // 256 != addr // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(4)
    return execute

def executeANDIndirectIndexed(cpu, memory, offsetRegister):
    def executeX():
        cpu.incrementPC().fetchInstruction()
        lookupAddr = (cpu.currentInstruction + cpu.getRegister("X")) & 0xFF
        lookupAddrNext = (lookupAddr + 1) & 0xFF
        addrLo = memory.getByte(lookupAddr)
        addrHi = memory.getByte(lookupAddrNext)
        addr = addrHi << 8 | addrLo
        operand = memory.getByte(addr)
        a = cpu.getRegister("A")
        result8 = a & operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        cpu.incrementPC().addClockCyclesThisCycle(6)
    def executeY():
        cpu.incrementPC().fetchInstruction()
        addrLo = memory.getByte(cpu.currentInstruction)
        addrHi = memory.getByte(cpu.currentInstruction + 1)
        addr = addrHi << 8 | addrLo
        addrOffset = (addr + cpu.getRegister("Y")) & 0xFFFF
        operand = memory.getByte(addrOffset)
        a = cpu.getRegister("A")
        result8 = a & operand
        cpu.setRegister("A", result8)
        setZNFlags(result8, cpu)
        if addr // 256 != addrOffset // 256: cpu.addClockCyclesThisCycle(1)
        cpu.incrementPC().addClockCyclesThisCycle(5)
    return executeX if offsetRegister == "X" else executeY