import pandas as pd

from config.config import TradingConfig
from .cpr import CPRCalculator, CPRLevels
from .ema import EMACalculator
from .pivot_ranges import PivotCalculator, PivotLevels
from ..data.data_loader import DataLoader


class SignalGenerator:
    def __init__(self, config: 'TradingConfig'):
        self.config = config
        self.data_loader = DataLoader(
            config.symbol,
            config.start_date,
            config.end_date
        )

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on CPR, Pivot Ranges, and EMA"""
        signals = pd.DataFrame(index=data.index)

        # Calculate EMAs
        signals['EMA_short'] = EMACalculator.calculate(
            data['Close'],
            self.config.ema_short
        )
        signals['EMA_long'] = EMACalculator.calculate(
            data['Close'],
            self.config.ema_long
        )

        signals['signal'] = 0

        for i in range(1, len(data)):
            # Calculate CPR using previous day's data
            cpr = CPRCalculator.calculate(
                data['High'].iloc[i - 1],
                data['Low'].iloc[i - 1],
                data['Close'].iloc[i - 1]
            )

            # Calculate Pivot Ranges
            pivot_levels = PivotCalculator.calculate(
                data['High'].iloc[i - 1],
                data['Low'].iloc[i - 1],
                data['Close'].iloc[i - 1]
            )

            # Current price and volume data
            price = data['Close'].iloc[i]
            volume = data['Volume'].iloc[i]
            avg_volume = data['Volume'].iloc[i - 20:i].mean()

            if self._check_entry_conditions(
                    price,
                    cpr,
                    pivot_levels,
                    signals['EMA_short'].iloc[i],
                    signals['EMA_long'].iloc[i],
                    volume,
                    avg_volume
            ):
                signals.loc[data.index[i], 'signal'] = 1

        return signals

    def _check_entry_conditions(
            self,
            price: float,
            cpr: CPRLevels,
            pivot_levels: PivotLevels,
            ema_short: float,
            ema_long: float,
            volume: float,
            avg_volume: float
    ) -> bool:
        """
        Check all conditions for trade entry including pivot ranges
        Returns True if all conditions are met
        """
        # Basic CPR and EMA conditions
        basic_conditions = (
                CPRCalculator.is_price_above_tc(price, cpr) and
                EMACalculator.is_bullish_crossover(ema_short, ema_long) and
                volume > (avg_volume * self.config.volume_threshold)
        )

        # Pivot range conditions
        pivot_conditions = self._check_pivot_conditions(price, pivot_levels)

        return basic_conditions and pivot_conditions

    def _check_pivot_conditions(self, price: float, pivot_levels: PivotLevels) -> bool:
        """
        Check price position relative to pivot levels
        Implement pivot-based trading rules
        """
        # Example pivot-based rules:
        # 1. Price should be above pivot point
        above_pivot = price > pivot_levels.pivot

        # 2. Check if price is not near major resistance levels (avoid entering near resistance)
        not_near_resistance = not any([
            PivotCalculator.is_price_near_level(price, pivot_levels.r1),
            PivotCalculator.is_price_near_level(price, pivot_levels.r2),
            PivotCalculator.is_price_near_level(price, pivot_levels.r3)
        ])

        # 3. Price should be above S1 for trend confirmation
        above_s1 = price > pivot_levels.s1

        return above_pivot and not_near_resistance and above_s1