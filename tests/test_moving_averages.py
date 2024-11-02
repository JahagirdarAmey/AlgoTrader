import unittest
import pandas as pd

from src.signals.ema import EMACalculator


class TestMovingAverages(unittest.TestCase):
    def test_ema_calculation(self):

        # Test case data
        data = pd.Series([1, 2, 3, 4, 5])
        period = 3

        # Calculate EMA
        ema = EMACalculator.calculate(data, period)

        # Verify ema is calculated
        self.assertEqual(len(ema), len(data))
        self.assertTrue(all(ema.notna()))