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