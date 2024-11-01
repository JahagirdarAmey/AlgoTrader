Feature: Technical Analysis Indicators
    As a trader
    I want to calculate technical indicators
    So that I can make informed trading decisions

    Background:
        Given I have market data for the last 30 days

    Scenario: Calculate RSI in an uptrend market
        Given the market is in an uptrend
        When I calculate the RSI
        Then the RSI should be above 60
        And the RSI values should be between 0 and 100

    Scenario: Calculate RSI in a downtrend market
        Given the market is in a downtrend
        When I calculate the RSI
        Then the RSI should be below 40
        And the RSI values should be between 0 and 100

    Scenario: Calculate VWAP
        Given I have price and volume data
        When I calculate the VWAP
        Then the VWAP should follow the price trend
        And the VWAP should consider volume weight

    Scenario Outline: Calculate Bollinger Bands with different standard deviations
        Given I have closing price data
        When I calculate Bollinger Bands with <std_dev> standard deviations
        Then the upper band should be above the lower band
        And the bands should contain <percentage> of prices

        Examples:
            | std_dev | percentage |
            | 2       | 95        |
            | 3       | 99        |

    Scenario: Calculate ATR in volatile market
        Given the market is volatile
        When I calculate the ATR
        Then the ATR should be higher than normal
        And the ATR should be positive

    Scenario: Handle missing data
        Given I have market data with missing values
        When I calculate all indicators
        Then the indicators should handle missing values gracefully
        And appropriate warnings should be logged