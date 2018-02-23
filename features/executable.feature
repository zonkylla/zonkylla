Feature: Zonkylla executable

  Scenario: Running zonkylla prints out help
    Given we have zonkylla installed
    When we run "zonkylla"
    Then return code is "1"
    And we see "zonkylla" on stderr
