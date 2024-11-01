from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class TradingConfig:
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    ema_short: int
    ema_long: int
    volume_threshold: float
    stop_loss: float
    take_profit: float
    pivot_threshold: float = 0.001  # New parameter for pivot level proximity

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TradingConfig':
        return cls(**config_dict)