# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                       |    Stmts |     Miss |   Cover |   Missing |
|--------------------------- | -------: | -------: | ------: | --------: |
| src/cached\_decorator.py   |       51 |        2 |     96% |   91, 100 |
| src/calendar\_data.py      |      118 |        1 |     99% |        79 |
| src/calendar\_image.py     |      163 |        9 |     94% |17-18, 272, 312-315, 322, 328, 410 |
| src/google\_calendar.py    |       89 |       63 |     29% |22-26, 29-48, 51-54, 63, 66-72, 81-120, 123, 126, 129, 138-152 |
| src/image\_loader.py       |       17 |        0 |    100% |           |
| src/iot\_calendar.py       |      106 |       40 |     62% |42-45, 54-57, 59-70, 100-125, 133, 154 |
| src/openweathermap\_org.py |       63 |        0 |    100% |           |
| src/singleton.py           |        9 |        0 |    100% |           |
| src/svg\_to\_png.py        |       16 |       11 |     31% |10-12, 37-44 |
| src/weather\_gov.py        |       30 |       25 |     17% |     28-65 |
|                  **TOTAL** |  **662** |  **151** | **77%** |           |


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