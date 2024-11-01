# tests/step_defs/test_technical_analysis_steps.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import numpy as np
import logging

# Import all scenarios from the feature file
scenarios('../features/technical_analysis.feature')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RSI Steps
@when("I calculate the RSI")
def calculate_rsi(context, market_data, analyzer):
    context['rsi'] = analyzer.calculate_rsi(market_data)

@then(parsers.parse("the RSI should be {condition} {value:d}"))
def check_rsi_condition(context, condition, value):
    rsi_value = context['rsi'].iloc[-1]
    if condition == "above":
        assert rsi_value > value, f"RSI should be above {value}, got {rsi_value}"
    elif condition == "below":
        assert rsi_value < value, f"RSI should be below {value}, got {rsi_value}"

@then("the RSI values should be between 0 and 100")
def check_rsi_range(context):
    rsi_values = context['rsi'].dropna()
    assert all(0 <= x <= 100 for x in rsi_values), "RSI values outside valid range"

# VWAP Steps
@when("I calculate the VWAP")
def calculate_vwap(context, market_data, analyzer):
    context['vwap'] = analyzer.calculate_vwap(market_data)

@then("the VWAP should follow the price trend")
def check_vwap_trend(context, market_data):
    correlation = market_data['Close'].corr(context['vwap'])
    assert correlation > 0.8, f"VWAP not following price trend, correlation: {correlation}"

# Bollinger Bands Steps
@when(parsers.parse("I calculate Bollinger Bands with {std_dev:d} standard deviations"))
def calculate_bollinger_bands(context, market_data, analyzer, std_dev):
    context['upper_band'], context['lower_band'] = analyzer.calculate_bollinger_bands(
        market_data, std_dev=std_dev
    )

@then("the upper band should be above the lower band")
def check_bands_order(context):
    assert all(context['upper_band'] >= context['lower_band']), "Band order violation"

@then(parsers.parse("the bands should contain {percentage:d} of prices"))
def check_bands_coverage(context, market_data, percentage):
    prices = market_data['Close']
    within_bands = ((prices >= context['lower_band']) &
                   (prices <= context['upper_band'])).mean() * 100
    assert within_bands >= percentage - 5, f"Expected {percentage}% within bands, got {within_bands:.1f}%"

# ATR Steps
@when("I calculate the ATR")
def calculate_atr(context, market_data, analyzer):
    context['atr'] = analyzer.calculate_atr(market_data)

@then("the ATR should be higher than normal")
def check_atr_volatility(context):
    atr_mean = context['atr'].mean()
    atr_baseline = context['atr'].iloc[0]  # First ATR value as baseline
    assert atr_mean > atr_baseline, "ATR not reflecting increased volatility"

# Missing Data Steps
@given("I have market data with missing values", target_fixture="market_data")
def market_data_with_gaps(data_generator):
    return data_generator.create_market_data(days=30, include_gaps=True)

@when("I calculate all indicators")
def calculate_all_indicators(context, market_data, analyzer):
    with pytest.warns(RuntimeWarning) as warning_info:
        context['result'] = analyzer.add_all_indicators(market_data)
    context['warnings'] = warning_info

@then("appropriate warnings should be logged")
def check_warnings_logged(context):
    assert len(context['warnings']) > 0, "No warnings generated for missing values"
    for warning in context['warnings']:
        logger.info(f"Warning captured: {warning.message}")