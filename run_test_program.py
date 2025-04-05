from cpu import CPU
from memory import Memory
import os
DIR = os.path.dirname(os.path.abspath(__file__))

memory = Memory()
cpu = CPU(memory)


with open(os.path.join(DIR, "testProgram", "6502_functional_test.bin"), "rb") as file:
    bin_arr = []
    while (byte := file.read(1)):
        bin_arr.append(int.from_bytes(byte))

    with open(os.path.join(DIR, "testProgram", "bindecoded"), "w") as file:
        for i in range(len(bin_arr)):
            file.write(hex(i) + ": " + hex(bin_arr[i]) + ", ")
            if i % 10 == 0: file.write("\n")
    memory.setBytes(0x00, bin_arr)
    cpu.reset()
    
    loops = 0
    while loops < 10:
        cpu.runSingleInstructionCycle()
        print(hex(cpu.currentInstruction))
        print()
        print(cpu)
        loops += 1
    
    print("!!!\n\n")
    cpu.setRegister("PC", 0x0400)
    loops = 0

    for x in range(10):
        print(hex(bin_arr[0x0400 + x]))
    print()

    while loops < 10:
        cpu.runSingleInstructionCycle()
        print(hex(cpu.currentInstruction))
        print()
        print(cpu)
        loops += 1

