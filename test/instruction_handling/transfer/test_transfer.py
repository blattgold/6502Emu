import unittest
from cpu import CPU
from memory import Memory

class TestTransferInstructions(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory, test=True)
        self.cpu.reset()

    def test_correct_cycles(self):
        self.memory.set_byte(0x1000, 0xAA)
        state = self.cpu.run()
        self.assertEqual(state.get_by_id("clock_cycles"), 2)