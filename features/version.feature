Feature: Zonkylla version

  Scenario: Write version number to stdout
    Given we have zonkylla installed
    When we run "zonkylla --version"
    Then return code is "0"
    And we see "0.0.2" on stdout
