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