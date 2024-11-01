Feature: Signal Generation
  As a trader
  I want to generate trading signals based on technical indicators
  So that I can make informed trading decisions

  Scenario: Generate buy signal
    Given the price crosses above TC
    And short EMA is above long EMA
    And volume is above threshold
    When I check for signals
    Then a buy signal should be generated

  Scenario: No signal conditions
    Given the price is below TC
    When I check for signals
    Then no signal should be generated

# tests/features/trade_execution.feature
Feature: Trade Execution
  As a trader
  I want to execute trades based on signals
  So that I can manage my positions effectively

  Scenario: Enter long position
    Given there is no open position
    And a valid buy signal is generated
    When I process the signal
    Then a long position should be opened
    And stop loss and take profit levels should be set

  Scenario: Hold position
    Given I have an open position
    And the price is between stop loss and take profit
    When I process the next signal
    Then the position should be maintained