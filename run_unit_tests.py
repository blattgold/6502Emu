import unittest
import os

suite = unittest.defaultTestLoader.discover(
    start_dir="test",
    pattern="test_*.py",
    top_level_dir=os.path.dirname(__file__)
)

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
