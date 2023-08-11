# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                       |    Stmts |     Miss |   Cover |   Missing |
|--------------------------- | -------: | -------: | ------: | --------: |
| src/cached\_decorator.py   |       34 |        1 |     97% |        96 |
| src/cached\_image.py       |       15 |        9 |     40% |     19-27 |
| src/calendar\_data.py      |      120 |        2 |     98% |   79, 261 |
| src/calendar\_image.py     |      167 |       63 |     62% |17-18, 253, 300-380, 420 |
| src/google\_calendar.py    |       99 |       72 |     27% |22-26, 29-48, 51-54, 63, 66-72, 81-120, 123, 126, 129, 138-152, 156-164 |
| src/iot\_calendar.py       |      112 |       75 |     33% |40-73, 78-86, 89-93, 99-124, 129-143, 152-165, 169-177 |
| src/openweathermap\_org.py |       74 |       60 |     19% |30-31, 34-39, 47-73, 90-145, 154-166 |
| src/singleton.py           |        6 |        3 |     50% |     10-12 |
| src/svg\_to\_png.py        |       22 |       15 |     32% |10-12, 16-33, 37-44, 49 |
| src/weather\_gov.py        |       34 |       28 |     18% |28-65, 74-76 |
|                  **TOTAL** |  **683** |  **328** | **52%** |           |


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