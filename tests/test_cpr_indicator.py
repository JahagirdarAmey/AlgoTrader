import unittest

from src.signals.cpr import CPRCalculator


class TestCPRIndicator(unittest.TestCase):

    def test_cpr_calculation(self):
        # Test case data
        high, low, close = 100.0, 90.0, 95.0

        # Calculate CPR
        cpr = CPRCalculator.calculate(high, low, close)

        # Verify calculations
        expected_pivot = (high + low + close) / 3
        expected_bc = (high + low) / 2
        expected_tc = (expected_pivot - expected_bc) + expected_pivot

        self.assertEqual(cpr.pivot, expected_pivot)
        self.assertEqual(cpr.bc, expected_bc)
        self.assertEqual(cpr.tc, expected_tc)

    def test_cpr_calculation_with_zeros(self):
        # Test case data
        high, low, close = 0, 0, 0.000000000

        # Calculate CPR
        cpr = CPRCalculator.calculate(high, low, close)


        self.assertEqual(cpr.pivot, 0)
        self.assertEqual(cpr.bc, 0)
        self.assertEqual(cpr.tc, 0)

