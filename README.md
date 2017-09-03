zonkylla
========

Tool for zonky.cz

Usage
-----

-   Run

    ``` bash
    $ virtualenv-3.6 venv
    $ source venv/bin/activate
    $ python setup.py install
    $ python -m zonkylla
    $ deactivate
    ```

-   Testing run with mock

    ``` bash
    echo 'test' | python -m zonkylla -t test
    ```
