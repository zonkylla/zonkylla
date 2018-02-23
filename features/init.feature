Feature: Zonkylla init

  Scenario: Zonkylla init on non-existend database
    Given we have zonkylla installed
    And we have zonkylla configured properly
    And there is no "./.zonkylla.db" file here
    When we run "zonkylla init"
    Then return code is "0"
    And file "./.zonkylla.db" is created
    And there is proper database structure within file "./.zonkylla.db"
    And we see "The database schema was created within file './.zonkylla.db'" on stdout
    And we see "Schema version is 3" on stdout

  Scenario: Zonkylla init on existing file (without structure)
    Given we have zonkylla installed
    And we have zonkylla configured properly
    And there is empty file "./.zonkylla.db"
    When we run "zonkylla init"
    Then return code is "1"
    And we see "Invalid database structure, remove file './.zonkylla.db', please." on stderr

  Scenario: Zonkylla init on existing file (with old structure)
    Given we have zonkylla installed
    And we have zonkylla configured properly
    And there is file "./.zonkylla.db" with old structure
    When we run "zonkylla init"
    Then return code is "1"
    And we see "Old version of database schema, remove file './.zonkylla.db', please." on stderr
