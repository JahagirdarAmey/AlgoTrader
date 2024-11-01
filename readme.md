# AlgoTrader 


```
# To install packages from requirements.txt

pip install -r requirements.txt
```


# Project Structure
```
AlgoTrader/
├── config/
│   └── config.py
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_loader.py
│   ├── signals/
│   │   ├── __init__.py
│   │   ├── cpr.py
│   │   ├── ema.py
│   │   └── signal_generator.py
│   ├── backtesting/
│   │   ├── __init__.py
│   │   └── backtest.py
│   └── trade_execution/
│       ├── __init__.py
│       └── trade_manager.py
├── tests/
│   ├── features/
│   │   ├── backtest.feature
│   │   ├── signal_generation.feature
│   │   └── trade_execution.feature
│   └── steps/
│       ├── __init__.py
│       ├── backtest_steps.py
│       ├── signal_steps.py
│       └── trade_steps.py
└── main.py
```