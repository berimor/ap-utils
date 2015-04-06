import sys
import unittest

import test_helpers


def suite():
    suites = ( test_helpers.suite(),
             )
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 100)
