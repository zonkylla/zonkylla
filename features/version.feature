Feature: Zonkylla version

  Scenario: Write version number to stdout
    Given we have zonkylla installed
    When we run "zonkylla --version"
    Then we see "0.0.1" on stdout
