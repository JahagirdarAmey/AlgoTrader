Feature: Backtesting
  As a trader
  I want to backtest my trading strategy
  So that I can evaluate its performance

  Background:
    Given I have historical market data
    And I have configured my trading parameters

  Scenario: Run basic backtest
    When I run the backtest
    Then it should calculate all trades correctly
    And generate performance metrics

  Scenario: Handle multiple trades
    Given I have a sequence of valid trading signals
    When I run the backtest
    Then it should execute trades according to the rules
    And maintain accurate position tracking

  Scenario: Calculate performance metrics
    Given I have completed a backtest
    When I analyze the results
    Then I should see the following metrics:
      | Metric         | Type    |
      | Total trades   | Integer |
      | Win rate       | Float   |
      | Total profit   | Float   |
      | Max drawdown   | Float   |
      | Sharpe ratio   | Float   |