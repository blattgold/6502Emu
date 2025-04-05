from cpu import CPU
from memory import Memory

memory = Memory()
cpu = CPU(memory)

#TODO JMP tests
#TODO CLD tests

def testADCImm():
    # overflow, zero, carry and negative
    memory.setBytes(0x1000, [0x69, 12, 0x69, 128, 0x69, 64, 0x69, 1, 0x69, 0])
    
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("A") == 15)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 0)
    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 64)
    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    assert(cpu.runSingleInstructionCycle() ==2)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    cpu.setFlag("carry", True)
    assert(cpu.runSingleInstructionCycle() ==2)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))

def testADCZeroPage():
    # overflow, zero, carry and negative
    memory.setBytes(0x1000, [0x65, 0x30, 0x65, 0x31, 0x65, 0x32, 0x65, 0x33, 0x65, 0x34])
    memory.setBytes(0x30, [12, 128, 64, 1, 0])
    
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 15)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 0)
    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 64)
    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    cpu.setFlag("carry", True)
    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))

def testADCZeroPageX():
    # overflow, zero, carry and negative
    memory.setBytes(0x1000, [0x75, 0x30, 0x75, 0x30, 0x75, 0x31, 0x75, 0x32, 0x75, 0x33, 0x75, 0x34])
    memory.setBytes(0x30, [12, 128, 64, 1, 0])
    
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 15)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("X", 1)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 131)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("X", 0)

    cpu.setRegister("A", 0)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 64)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    cpu.setFlag("carry", True)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))

def testADCAbsolute():
    # overflow, zero, carry and negative
    memory.setBytes(0x1000, [0x6D, 0x30, 0x30, 0x6D, 0x31, 0x30, 0x6D, 0x32, 0x30, 0x6D, 0x33, 0x30, 0x6D, 0x34, 0x30])
    memory.setBytes(0x3030, [12, 128, 64, 1, 0])
    
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 15)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 0)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 64)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    cpu.setFlag("carry", True)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))

def testADCAbsoluteIndexed():
    # overflow, zero, carry and negative
    memory.setBytes(0x1000, [
        0x7D, 0x30, 0x30, 
        0x7D, 0x30, 0x30, 
        0x79, 0x30, 0x30,
        0x7D, 0xFF, 0x00, 
        0x79, 0xFF, 0x00, 
        0x7D, 0x31, 0x30, 
        0x7D, 0x32, 0x30, 
        0x7D, 0x33, 0x30, 
        0x7D, 0x34, 0x30
    ])
    memory.setBytes(0x3030, [12, 128, 64, 1, 0])
    memory.setByte(0x0100, 100)
    
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 15)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("X", 1)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 131)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("X", 0)

    cpu.setRegister("Y", 1)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 131)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("Y", 0)

    cpu.setRegister("X", 1)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 103)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("X", 0)

    cpu.setRegister("Y", 1)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 103)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("Y", 0)

    cpu.setRegister("A", 0)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 64)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    cpu.setFlag("carry", True)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))

def testADCIndirect():
    # overflow, zero, carry and negative
    memory.setBytes(0x1000, [
        0x61, 0x30, 
        0x61, 0x32, 
        0x61, 0x34, 
        0x61, 0x36, 
        0x61, 0x38,
        0x61, 0x30,

        0x71, 0x30, 
        0x71, 0x32, 
        0x71, 0x34,
        0x71, 0x36, 
        0x71, 0x38,
        0x71, 0x30,
        0x71, 0x3A,
    ])
    memory.setBytes(0x30, [
        0x00, 0x11,
        0x01, 0x11,
        0x02, 0x11,
        0x03, 0x11,
        0x04, 0x11,
        0xFF, 0x11,
    ])

    memory.setBytes(0x1100, [
        12, 
        128, 
        64, 
        1, 
        0
    ])
    memory.setByte(0x1200, 80)
    
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 15)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 0)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 64)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    cpu.setFlag("carry", True)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("X", 2)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 131)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("X", 0)




    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 15)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 0)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 64)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 128)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("A", 255)
    cpu.setFlag("carry", True)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 0)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()

    cpu.setRegister("Y", 1)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 131)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("Y", 0)

    cpu.setRegister("Y", 1)
    cpu.setRegister("A", 3)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 83)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))
    assert(not cpu.getFlag("carry"))
    assert(not cpu.getFlag("overflow"))
    cpu.resetFlags()
    cpu.setRegister("Y", 0)




def testLDAImm():
    memory.setBytes(0x1000, [0xA9, 0x45, 0xA9, 0x00, 0xA9, 0x80])

    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("A") == 0x45)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))

    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("A") == 0x00)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))

    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("A") == 0x80)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))

def testLDAZeroPage():
    memory.setBytes(0x1000, [0xA5, 0x57, 0xA5, 0x00, 0xA5, 0x80])
    memory.setBytes(0x56, [12, 97, 201])
    memory.setByte(0x80, 0x80)

    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 97)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))

    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 0x00)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))

    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("A") == 0x80)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))

def testLDAZeroPageX():
    memory.setBytes(0x1000, [0xB5, 0x57, 0xB5, 0x58, 0xB5, 0x59])
    memory.setBytes(0x56, [10, 66, 233, 12, 0, 0x80])
    cpu.setRegister("X", 2)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 12)
    assert(not cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))

    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0x00)
    assert(cpu.getFlag("zero"))
    assert(not cpu.getFlag("negative"))

    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0x80)
    assert(not cpu.getFlag("zero"))
    assert(cpu.getFlag("negative"))

def testLDAAbsolute():
    memory.setBytes(0x1000, [0xAD, 0x22, 0x33, 0xAD, 0x23, 0x33])
    memory.setBytes(0x3321, [10, 30, 60])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 30)
    cpu.runSingleInstructionCycle()
    assert(cpu.getRegister("A") == 60)

def testLDAAbsoluteX():
    memory.setBytes(0x1000, [0xBD, 0x22, 0x33, 0xBD, 0x23, 0x33, 0xBD, 0xFE, 0x00, 0xBD, 0xFF, 0x00, 0xBD, 0xFF, 0x01])
    memory.setBytes(0x3322, [10, 30, 60])
    memory.setBytes(0xFE, [0x20, 0x80, 0xA0])
    memory.setBytes(0x1FE, [12, 24, 36])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 10)
    cpu.setRegister("X", 1)
    cpu.runSingleInstructionCycle()
    assert(cpu.getRegister("A") == 60)

    # crossing page boundary should cause another cycle
    # LDA $254,X(1) -> $255 (4 cycles)
    # LDA $254,X(2) -> $256 (5 cycles)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0x80)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 0xA0)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 36)

def testLDAAbsoluteY():
    memory.setBytes(0x1000, [0xB9, 0x22, 0x33, 0xB9, 0x23, 0x33, 0xB9, 0xFE, 0x00, 0xB9, 0xFF, 0x00, 0xB9, 0xFF, 0x01])
    memory.setBytes(0x3322, [10, 30, 60])
    memory.setBytes(0xFE, [0x20, 0x80, 0xA0])
    memory.setBytes(0x1FE, [12, 24, 36])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 10)
    cpu.setRegister("Y", 1)
    cpu.runSingleInstructionCycle()
    assert(cpu.getRegister("A") == 60)

    # crossing page boundary should cause another cycle
    # LDA $254,X(1) -> $255 (4 cycles)
    # LDA $254,X(2) -> $256 (5 cycles)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("A") == 0x80)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 0xA0)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 36)

def testLDAIndirectX():
    memory.setBytes(0x1000, [0xA1, 0x22, 0xA1, 0x22])
    memory.setBytes(0x22, [0x33, 0x33, 0x44])
    memory.setByte(0x3333, 77)
    memory.setByte(0x4433, 88)

    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 77)
    cpu.setRegister("X", 1)
    assert(cpu.runSingleInstructionCycle() == 6)
    print(cpu.getRegister("A"))
    assert(cpu.getRegister("A") == 88)

def testLDAIndirectY():
    memory.setBytes(0x1000, [0xB1, 0x22, 0xB1, 0x22])
    memory.setBytes(0x22, [0xFF, 0x33, 0x55, 0x33])
    memory.setByte(0x33FF, 77)
    memory.setByte(0x3400, 88)

    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("A") == 77)

    cpu.setRegister("Y", 1)
    assert(cpu.runSingleInstructionCycle() == 6)
    assert(cpu.getRegister("A") == 88)

# LDX

def testLDXImm():
    memory.setBytes(0x1000, [0xA2, 129])
    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("X") == 129)

def testLDXZeroPage():
    memory.setBytes(0x1000, [0xA6, 0x12])
    memory.setBytes(0x11, [12, 55, 88])
    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("X") == 55)

def testLDXZeroPageY():
    memory.setBytes(0x1000, [0xB6, 0x12, 0xB6, 0x12])
    memory.setBytes(0x11, [12, 55, 88])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("X") == 55)
    cpu.setRegister("Y", 1)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("X") == 88)

def testLDXAbsolute():
    memory.setBytes(0x1000, [0xAE, 0x33, 0x22])
    memory.setBytes(0x2232, [0x11, 0x22, 0x33])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("X") == 0x22)

def testLDXAbsoluteY():
    memory.setBytes(0x1000, [0xBE, 0xFF, 0x22, 0xBE, 0xFF, 0x22])
    memory.setBytes(0x22FF, [0x20, 0x30])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("X") == 0x20)
    cpu.setRegister("Y", 1)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("X") == 0x30)

# LDY

def testLDYImm():
    memory.setBytes(0x1000, [0xA0, 129])
    assert(cpu.runSingleInstructionCycle() == 2)
    assert(cpu.getRegister("Y") == 129)

def testLDYZeroPage():
    memory.setBytes(0x1000, [0xA4, 0x12])
    memory.setBytes(0x11, [12, 55, 88])
    assert(cpu.runSingleInstructionCycle() == 3)
    assert(cpu.getRegister("Y") == 55)

def testLDYZeroPageY():
    memory.setBytes(0x1000, [0xB4, 0x12, 0xB4, 0x12])
    memory.setBytes(0x11, [12, 55, 88])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("Y") == 55)
    cpu.setRegister("X", 1)
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("Y") == 88)

def testLDYAbsolute():
    memory.setBytes(0x1000, [0xAC, 0x33, 0x22])
    memory.setBytes(0x2232, [0x11, 0x22, 0x33])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("Y") == 0x22)

def testLDYAbsoluteY():
    memory.setBytes(0x1000, [0xBC, 0xFF, 0x22, 0xBC, 0xFF, 0x22])
    memory.setBytes(0x22FF, [0x20, 0x30])
    assert(cpu.runSingleInstructionCycle() == 4)
    assert(cpu.getRegister("Y") == 0x20)
    cpu.setRegister("X", 1)
    assert(cpu.runSingleInstructionCycle() == 5)
    assert(cpu.getRegister("Y") == 0x30) 

tests = [
    testADCImm,
    testADCZeroPage,
    testADCZeroPageX,
    testADCAbsolute,
    testADCAbsoluteIndexed,
    testADCIndirect,
    testLDAImm,
    testLDAZeroPage,
    testLDAZeroPageX,
    testLDAAbsolute,
    testLDAAbsoluteX,
    testLDAAbsoluteY,
    testLDAIndirectX,
    testLDAIndirectY,
    testLDXImm,
    testLDXZeroPage,
    testLDXZeroPageY,
    testLDXAbsolute,
    testLDXAbsoluteY,
    testLDYImm,
    testLDYZeroPage,
    testLDYZeroPageY,
    testLDYAbsolute,
    testLDYAbsoluteY
]

def testAll():
    for test in tests:
        cpu.resetAllRegisters()
        memory.resetMemory()
        cpu.reset()
        test()
        print("test passed: " + test.__name__)

if __name__ == "__main__":
    testAll()
