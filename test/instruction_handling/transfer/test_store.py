import unittest
import random
from abc import ABC, abstractmethod
from functools import reduce

from cpu import CPU
from memory import Memory

class StoreCommon(ABC, unittest.TestCase):
    expected_cycles = 0

    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory, test=True)
        self.cpu_state_init = self.cpu.state
        self.cpu.reset()
    
    def _run_test_cycles(
        self, 
        opcode: int, 
        r_from: str, 
        **kwargs
    ):
        self.cpu.reset_state()
        self.cpu.state.set_by_id("pc", 0x1000)
        self.memory.set_bytes(0x1000, [opcode, 0x10])
        state = self.cpu.run()
        self.assertEqual(state.get_by_id("clock_cycles"), self.expected_cycles)
    
    def _run_test_transfer(
        self, 
        opcode: int, 
        r_from: str, 
        val: int, 
        addr: int, 
        expected_addr: int, 
        expected_val: int, 
        **kwargs
    ):
        self.cpu.reset_state()
        self.cpu.state.set_by_id("pc", 0x1000)
        self.memory.set_bytes(0x1000, [opcode, addr &0xFF, addr >> 8] if addr > 255 else [opcode, addr])
        self.cpu.state.set_by_id(r_from, val)
        state = self.cpu.run()
        self.assertEqual(expected_val, self.memory.get_byte(expected_addr))
    
    def _run_test_transfer_indexed(
        self,
        opcode: int, 
        r_from: str, 
        r_index: str, 
        val: int, 
        addr: int,
        index: int, 
        expected_addr: int, 
        expected_val: int,
        **kwargs
    ):
        self.cpu.reset_state()
        self.cpu.state.set_by_id("pc", 0x1000)

        # split addr into two if bigger than 255
        self.memory.set_bytes(0x1000, [opcode, addr &0xFF, addr >> 8] if addr > 255 else [opcode, addr])

        self.cpu.state.set_by_id(r_from, val)
        self.cpu.state.set_by_id(r_index, index)

        state = self.cpu.run()
        self.assertEqual(self.cpu.memory.get_byte(expected_addr), expected_val)


class TestStoreInstructionsZP(StoreCommon):
    expected_cycles = 3

    def _gen_test_params(self, exclude=[]):
        return [
            {"opcode": 0x86, "r_from": "X"},
            {"opcode": 0x84, "r_from": "Y"},
            {"opcode": 0x85, "r_from": "A"}
        ]

    def test_all_cycles(self):
        for test in self._gen_test_params():
            self._run_test_cycles(**test)
    
    def test_all_transfer(self):
        for test in self._gen_test_params():
            addr = random.randint(0, 255)
            val = random.randint(0, 255)
            self._run_test_transfer(**test, val=val, addr=addr, expected_addr=addr, expected_val=val)

class TestStoreInstructionsZPI(TestStoreInstructionsZP):
    expected_cycles = 4

    def _gen_test_params(self):
        return [
            {"opcode": 0x96, "r_from": "X", "r_index": "Y"},
            {"opcode": 0x94, "r_from": "Y", "r_index": "X"},
            {"opcode": 0x95, "r_from": "A", "r_index": "X"}
        ]

    def test_all_transfer_indexed(self):
        for test in self._gen_test_params():
            addr = random.randint(0, 255)
            val = random.randint(0, 255)
            index = random.randint(0, 255)
            self._run_test_transfer_indexed(**test, val=val, addr=addr, index=index, expected_addr=(addr + index) &0xFF, expected_val= val)
    
    def test_all_edge_cases(self):
        def run_test(
            opcode: int, 
            r_from: str, 
            r_index: str, 
            val: int, 
            addr: int, 
            index: int,
            **kwargs
        ):
            self.cpu.reset_state()
            expected_effective_addr = (addr + index) &0xFF

            self.cpu.state.set_by_id("pc", 0x1000)
            self.memory.set_bytes(0x1000, [opcode, addr])

            self.cpu.state.set_by_id(r_from, val)
            self.cpu.state.set_by_id(r_index, index)

            state = self.cpu.run()
            self.assertEqual(self.cpu.memory.get_byte(expected_effective_addr), val)
        
        for test in self._gen_test_params():
            run_test(**test, val=0xFF, addr=0x00, index=0x00)
            run_test(**test, val=0xFF, addr=0xFF, index=0x00)
            run_test(**test, val=0xFF, addr=0x00, index=0xFF)
            run_test(**test, val=0xFF, addr=0xFF, index=0xFF)

class TestStoreInstructionsABS(StoreCommon):
    expected_cycles = 4

    def _gen_test_params(self):
        return [
            {"opcode": 0x8E, "r_from": "X"},
            {"opcode": 0x8C, "r_from": "Y"},
            {"opcode": 0x8D, "r_from": "A"}
        ]
    
    def test_all_cycles(self):
        for test in self._gen_test_params():
            self._run_test_cycles(**test)
    
    def test_all_transfer(self):
        for test in self._gen_test_params():
            addr = random.randint(256, 65535)
            val = random.randint(0, 255)
            self._run_test_transfer(**test, val=val, addr=addr, expected_addr=addr, expected_val=val)

# ABI TODO
# IND TODO