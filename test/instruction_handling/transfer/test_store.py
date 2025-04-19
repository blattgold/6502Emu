import unittest
import random
from cpu import CPU
from memory import Memory

class StoreCommon(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory, test=True)
        self.cpu_state_init = self.cpu.state
        self.cpu.reset()

class TestStoreInstructionsZP(StoreCommon):
    # ZP
    def _gen_test_params(self):
        return (
            (0x86, "X"),
            (0x84, "Y"),
            (0x85, "A")
        )

    def test_all_cycles(self):
        def run_test(opcode: int):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, 0x10])
            state = self.cpu.run()
            self.assertEqual(state.get_by_id("clock_cycles"), 3)
        
        for test in self._gen_test_params():
            run_test(test[0])
    
    def test_all_transfer(self):
        def run_test(opcode: int, r_from: str, val: int, addr: int):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, addr])
            self.cpu.state.set_by_id(r_from, val)
            state = self.cpu.run()
            self.assertEqual(val, self.memory.get_byte(addr))

        for test in self._gen_test_params():
            run_test(*test, val=random.randint(0, 255), addr=random.randint(0, 255))

class TestStoreInstructionsZPI(StoreCommon):
    def _gen_test_params(self):
        return (
            (0x96, "X", "Y"),
            (0x94, "Y", "X"),
            (0x95, "A", "X")
        )
    
    def test_all_cycles(self):
        def run_test(opcode: int):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, 0x10])
            state = self.cpu.run()
            self.assertEqual(state.get_by_id("clock_cycles"), 4)
        
        for test in self._gen_test_params():
            run_test(test[0])

    def test_all_transfer(self):
        def run_test(opcode: int, r_from: str, r_index: str, val: int, addr: int):
            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, addr])
            self.cpu.state.set_by_id(r_from, val)
            state = self.cpu.run()
            self.assertEqual(self.cpu.memory.get_byte(addr), val)
        
        for test in self._gen_test_params():
            self.cpu.reset_state()
            run_test(*test, val=random.randint(0, 255), addr=random.randint(0, 255))

    def test_all_transfer_indexed(self):
        def run_test(opcode: int, r_from: str, r_index: str, val: int, addr: int, index: int):
            self.cpu.reset_state()
            expected_effective_addr = (addr + index) &0xFF

            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, addr])

            self.cpu.state.set_by_id(r_from, val)
            self.cpu.state.set_by_id(r_index, index)

            state = self.cpu.run()
            self.assertEqual(self.cpu.memory.get_byte(expected_effective_addr), val)
        
        for test in self._gen_test_params():
            run_test(*test, val=random.randint(0, 255), addr=random.randint(0, 255), index=random.randint(0, 255))
    
    def test_all_edge_cases(self):
        def run_test(opcode: int, r_from: str, r_index: str, val: int, addr: int, index: int):
            self.cpu.reset_state()
            expected_effective_addr = (addr + index) &0xFF

            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, addr])

            self.cpu.state.set_by_id(r_from, val)
            self.cpu.state.set_by_id(r_index, index)

            state = self.cpu.run()
            self.assertEqual(self.cpu.memory.get_byte(expected_effective_addr), val)
        
        for test in self._gen_test_params():
            run_test(*test, val=0xFF, addr=0x00, index=0x00)
            run_test(*test, val=0xFF, addr=0xFF, index=0x00)
            run_test(*test, val=0xFF, addr=0x00, index=0xFF)
            run_test(*test, val=0xFF, addr=0xFF, index=0xFF)
# ABS TODO
# ABI TODO
# IND TODO