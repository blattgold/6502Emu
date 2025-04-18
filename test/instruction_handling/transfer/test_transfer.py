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
        self.assertEqual(
            self.cpu.run().get_state()["clock_cycles"],
            2
        )