Feature: Zonkylla update

  Scenario: Zonkylla update on non-existend database
    Given we have zonkylla installed
    And we have zonkylla configured properly
    And there is no "./.zonkylla.db" file here
    And we provided password "test_password"
    When we run "zonkylla -t update test_user"
    Then return code is "1"
    And we see "missing" on stderr
    And we see "zonkylla init" on stdout
