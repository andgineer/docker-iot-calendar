# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                       |    Stmts |     Miss |   Cover |   Missing |
|--------------------------- | -------: | -------: | ------: | --------: |
| src/cached\_decorator.py   |       51 |        2 |     96% |   93, 102 |
| src/calendar\_data.py      |      118 |        1 |     99% |        85 |
| src/calendar\_image.py     |      163 |        9 |     94% |19-20, 300, 344-347, 354, 363, 452 |
| src/google\_calendar.py    |       91 |       32 |     65% |32, 47-54, 89-135, 141, 144, 159, 169 |
| src/image\_loader.py       |       17 |        0 |    100% |           |
| src/iot\_calendar.py       |      100 |       22 |     78% |44-47, 56-59, 61-72, 134, 155 |
| src/openweathermap\_org.py |       63 |        0 |    100% |           |
| src/singleton.py           |        9 |        0 |    100% |           |
| src/svg\_to\_png.py        |       16 |       11 |     31% |11-13, 38-45 |
| src/weather\_gov.py        |       30 |       25 |     17% |     27-64 |
|                  **TOTAL** |  **658** |  **102** | **84%** |           |


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