# """
# run_tests.py
# Ejecuta manualmente los archivos de pruebas.
# """

# import unittest

# if __name__ == "__main__":
#     loader = unittest.TestLoader()
#     suite = loader.discover("tests")

#     runner = unittest.TextTestRunner(verbosity=2)
#     runner.run(suite)
"""
run_tests.py
Ejecuta manualmente los archivos de pruebas con pytest.
"""

import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "tests/"]))