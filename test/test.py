import unittest
from runner.TreeTextTestResult import TreeTextTestResult

if __name__ == "__main__":
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    runner = unittest.runner.TextTestRunner(verbosity=2, resultclass=TreeTextTestResult)
    runner.run(tests)
