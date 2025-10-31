# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                       |    Stmts |     Miss |   Cover |   Missing |
|--------------------------- | -------: | -------: | ------: | --------: |
| src/cached\_decorator.py   |       58 |        1 |     98% |       111 |
| src/calendar\_data.py      |      101 |        1 |     99% |        90 |
| src/calendar\_image.py     |      177 |       11 |     94% |104, 172, 179, 319, 419-422, 429, 438, 491, 506 |
| src/google\_calendar.py    |       90 |        5 |     94% |110, 115, 154, 158, 183 |
| src/image\_loader.py       |       19 |        0 |    100% |           |
| src/iot\_calendar.py       |      110 |        2 |     98% |  167, 207 |
| src/models.py              |        6 |        0 |    100% |           |
| src/openweathermap\_org.py |       63 |        0 |    100% |           |
| src/singleton.py           |       10 |        0 |    100% |           |
| src/weather\_gov.py        |       72 |       12 |     83% |46-50, 60, 73-76, 85, 89, 91, 93, 126 |
|                  **TOTAL** |  **706** |   **32** | **95%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/andgineer/docker-iot-calendar/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/andgineer/docker-iot-calendar/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fandgineer%2Fdocker-iot-calendar%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.