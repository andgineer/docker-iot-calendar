# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                       |    Stmts |     Miss |   Cover |   Missing |
|--------------------------- | -------: | -------: | ------: | --------: |
| src/cached\_decorator.py   |       59 |        2 |     97% |  108, 117 |
| src/calendar\_data.py      |      103 |        1 |     99% |        90 |
| src/calendar\_image.py     |      177 |       11 |     94% |105, 170, 177, 312, 409-412, 419, 428, 481, 494 |
| src/google\_calendar.py    |       90 |        5 |     94% |106, 111, 150, 154, 179 |
| src/image\_loader.py       |       19 |        0 |    100% |           |
| src/iot\_calendar.py       |      110 |        2 |     98% |  158, 199 |
| src/models.py              |       12 |        0 |    100% |           |
| src/openweathermap\_org.py |       63 |        0 |    100% |           |
| src/singleton.py           |       10 |        0 |    100% |           |
| src/weather\_gov.py        |       73 |       12 |     84% |43-46, 56, 65-68, 77, 81, 83, 85, 117 |
|                  **TOTAL** |  **716** |   **33** | **95%** |           |


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