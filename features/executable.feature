Feature: Zonkylla executable

  Scenario: Running zonkylla prints out help
    Given we have zonkylla installed
    When we run "zonkylla"
    Then we see "zonkylla" on stderr
