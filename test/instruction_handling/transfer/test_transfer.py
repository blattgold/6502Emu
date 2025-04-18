import unittest
import random
from cpu import CPU
from memory import Memory

class TestTransferInstructions(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory, test=True)
        self.cpu.reset()
    
    def _generate_tests(self):
        return (
            (0xAA, "A", "X"),
            (0xA8, "A", "Y"),
            (0xBA, "S", "X"),
            (0x8A, "X", "A"),
            (0x9A, "X", "S"),
            (0x98, "Y", "A"),
        )

    def test_all_cycles(self):
        def run_test(opcode: int, r_from: str, r_to: str):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_byte(0x1000, 0xAA)
            state = self.cpu.run()
            self.assertEqual(state.get_by_id("clock_cycles"), 2)
        
        for test in self._generate_tests():
            run_test(*test)
    
    
    def test_all_transfer(self):
        def run_test(opcode: int, r_from: str, r_to: str, num: int):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_byte(0x1000, opcode)
            self.cpu.state.set_by_id(r_from, num)
            state = self.cpu.run()
            self.assertEqual(state.get_by_id(r_to), num)

        for test in self._generate_tests():
            run_test(*test, num=random.randint(0, 255))
    
    def test_all_flags(self):
        def run_test(opcode: int, r_from: str, r_to: str, num: int, z_expected: bool, n_expected: bool):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_byte(0x1000, opcode)
            self.cpu.state.set_by_id(r_from, num)
            state = self.cpu.run()

            # transfers to S don't set flags
            if r_to != "S":
                self.assertEqual(state.get_by_id("Z"), z_expected)
                self.assertEqual(state.get_by_id("N"), n_expected)
        
        for test in self._generate_tests():
            run_test(*test, num=1,   z_expected=False, n_expected=False)
            run_test(*test, num=0,   z_expected=True,  n_expected=False)
            run_test(*test, num=128, z_expected=False, n_expected=True)
            run_test(*test, num=255, z_expected=False, n_expected=True)