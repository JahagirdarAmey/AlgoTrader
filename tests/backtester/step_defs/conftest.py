# tests/step_defs/conftest.py
import pytest
from pytest_bdd import given, parsers

from src.backtester import TechnicalAnalyzer
from tests.backtester.test_data.market_data_generator import MarketDataGenerator


# Shared fixtures
@pytest.fixture
def analyzer():
    """Provides a TechnicalAnalyzer instance"""
    return TechnicalAnalyzer()

@pytest.fixture
def context():
    """Provides a context dictionary to share data between steps"""
    return {}

@pytest.fixture
def data_generator():
    """Provides a MarketDataGenerator instance"""
    return MarketDataGenerator()

# Common given steps that can be reused across different feature files
@given("I have market data for the last 30 days", target_fixture="market_data")
def market_data(data_generator):
    return data_generator.create_market_data(days=30)

@given(parsers.parse("I have market data for the last {days:d} days"), target_fixture="market_data")
def market_data_with_days(data_generator, days):
    return data_generator.create_market_data(days=days)

@given("the market is in an uptrend", target_fixture="market_data")
def uptrend_market(data_generator):
    return data_generator.create_market_data(days=30, trend='up')

@given("the market is in a downtrend", target_fixture="market_data")
def downtrend_market(data_generator):
    return data_generator.create_market_data(days=30, trend='down')

@given("the market is volatile", target_fixture="market_data")
def volatile_market(data_generator):
    return data_generator.create_market_data(days=30, volatility='high')