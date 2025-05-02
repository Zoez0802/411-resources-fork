# Weather Dashboard Application 🌦️

## Overview

The Weather Dashboard is a web-based application that allows users to:
- **Create an account and log in securely**.
- **Save and manage a list of favorite locations** (cities).
- **View current weather, historical weather, and forecast information** for their favorite locations.
- **Remove locations** from their favorites list when needed.

The app integrates:
- **Flask** (web framework)
- **SQLite with SQLAlchemy** (for user authentication and database management)
- **OpenWeatherMap API** (for weather data)
- **In-memory model** (to track user-specific favorites)

## Features

- **Account Creation & Authentication**: Users can create accounts, log in, and securely manage their sessions.
- **Favorite Locations**: Users can add locations (cities) to their favorites list and view their current weather.
- **Weather Information**: Fetch current weather and historical weather data for favorite locations using the OpenWeatherMap API.
- **Remove Favorites**: Users can easily remove a location from their favorites when needed.

## Unit Tests

Unit tests for the weather dashboard app are provided in the `tests/` directory. The tests cover the functionality of the in-memory weather favorites model, including:

- **Adding single or multiple favorites**: Verifying users can add one or more locations to their list.
- **Preventing duplicate entries**: Ensuring the application handles duplicate locations properly (i.e., duplicates are allowed).
- **Removing favorites**: Tests for removing a location from the favorites, including edge cases like trying to remove non-existent favorites or favorites from unknown users.
- **Clearing all favorites**: Simulating the deletion of all favorite locations for a user.
- **Retrieving favorites**: Tests for retrieving favorites for both known and unknown users.

The test files include:
- **`test_weather_model.py`**: Covers tests for the weather model, handling favorite locations and weather data management.
- **`test_favorite_location.py`**: Focuses on adding, removing, and retrieving favorite locations for users.
- **`test_current_weather.py`**: Contains tests for adding and retrieving current weather data for favorite locations.
- **`test_user_model.py`**: Contains tests for user-related functionality, including account creation, login, and authentication.

### To run the tests locally:
```bash
pytest tests/test_weather_model.py
pytest tests/test_favorite_location.py
pytest tests/test_current_weather.py
pytest tests/test_user_model.py