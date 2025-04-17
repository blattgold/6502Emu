from cpu import CPU
from memory import Memory
import os
DIR = os.path.dirname(os.path.abspath(__file__))

memory = Memory()
cpu = CPU(memory)


with open(os.path.join(DIR, "testProgram", "6502_functional_test.bin"), "rb") as file:
    bin_arr = []
    byte = file.read(1)
    while byte:
        bin_arr.append(int.from_bytes(byte))
        byte = file.read(1)

    with open(os.path.join(DIR, "testProgram", "bindecoded"), "w") as file:
        for i in range(len(bin_arr)):
            file.write(hex(i) + ": " + hex(bin_arr[i]) + ", ")
            if i % 10 == 0: file.write("\n")
    memory.set_bytes(0x00, bin_arr)
    cpu.reset()
    
    print("\n")
    cpu.set_pc(0x3300)
    cpu.run()

