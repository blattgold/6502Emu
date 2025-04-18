import unittest
import random
from cpu import CPU
from memory import Memory

class TestStoreInstructions(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory, test=True)
        self.cpu.reset()
    
    def _generate_zp_tests(self):
        return (
            (0x86, "X"),
            (0x84, "Y"),
            (0x85, "A")
        )

    def test_zp_all_cycles(self):
        def run_test(opcode: int, r_from: str):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, 0x10])
            state = self.cpu.run()
            self.assertEqual(state.get_by_id("clock_cycles"), 3)
        
        for test in self._generate_zp_tests():
            run_test(*test)
    
    def test_zp_all_transfer(self):
        def run_test(opcode: int, r_from: str, num: int, addr: int):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, addr])
            self.cpu.state.set_by_id(r_from, num)
            state = self.cpu.run()
            self.assertEqual(num, self.memory.get_byte(addr))

        for test in self._generate_zp_tests():
            run_test(*test, num=random.randint(0, 255), addr=random.randint(0, 255))