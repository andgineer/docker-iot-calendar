# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web application that generates calendar images for Amazon Kindle displays, showing IoT device events from Google Calendar along with weather information. The app uses Tornado as the web server and matplotlib for image generation.

## Architecture

### Core Components

- **`src/iot_calendar.py`**: Main web server entry point using Tornado, handles HTTP routes and settings loading
- **`src/calendar_image.py`**: Core image generation using matplotlib, creates PNG calendar visualizations
- **`src/google_calendar.py`**: Google Calendar API integration for fetching events
- **`src/calendar_data.py`**: Data processing and calendar grid logic
- **`src/openweathermap_org.py`** & **`src/weather_gov.py`**: Weather data providers
- **`src/cached_decorator.py`**: Caching mechanism for API calls and image generation

### Data Flow

1. Settings loaded from `amazon-dash-private/settings.json`
2. Google Calendar events fetched via service account credentials
3. Weather data retrieved from OpenWeatherMap or Weather.gov
4. Data processed into weekly grids in `calendar_data.py`
5. Images generated using matplotlib in `calendar_image.py`
6. Served via Tornado web handlers

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (use two dots)
. ./activate.sh

# Install development dependencies
uv pip install -r requirements.dev.txt
```

### Testing
```bash
# Run all tests
make test
# or
python -m pytest tests/

# Run benchmarks
make bench
# or
python -m pytest --benchmark-json benchmark.json -m benchmark tests/
```

### Code Quality
```bash
# Run pre-commit hooks manually
pre-commit run --all-files

# Update dependencies
make reqs
```

### Local Development
```bash
# Run local server (requires amazon-dash-private folder with settings)
make run

# Direct Python execution for debugging
python src/iot_calendar.py
```

### Docker
```bash
# Build image
make build

# Run container (maps amazon-dash-private volume)
make run
```

## Configuration

- **Settings**: `amazon-dash-private/settings.json` - main configuration
- **Secrets**: Google Calendar service account JSON and OpenWeatherMap API key in `amazon-dash-private/`
- **Line length**: 100 characters (source), 99 characters (tests)
- **Code style**: Enforced via ruff with extensive rule set in `.pre-commit-config.yaml`

## Key External Dependencies

- **matplotlib**: Image generation with xkcd-style fonts
- **tornado**: Web server framework
- **google-api-python-client**: Google Calendar integration
- **requests**: Weather API calls
- **PIL/Pillow**: Image processing
- **numpy**: Numerical operations for matplotlib

## File Structure Notes

- `src/` - All Python source code
- `tests/` - pytest test suite
- `templates/` - Tornado HTML templates
- `static/` - Web assets (CSS, JS, images)
- `amazon-dash-private/` - Settings and secrets (not in repo)
- `docker/` - Docker configuration
