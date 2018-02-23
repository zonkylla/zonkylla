Feature: Status

  Scenario: Write status to stdout
    Given we have zonkylla installed
    And we have this data in wallet
        | availableBalance | blockedBalance | creditSum |
        |             1234 |            200 |      2400 |
    When we run "zonkylla status"
    Then return code is "0"
    And we see "1234" on stdout
    And we see "200" on stdout
    And we see "2400" on stdout
