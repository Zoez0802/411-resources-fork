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

## Weather Dashboard API Routes

### 1. **Add Favorite Location**
   - **Route**: `/api/favorites/add`
   - **Method**: `POST`
   - **Purpose**: Allows users to add a favorite location (city).
   - **Request Body**:
     ```json
     {
       "user_id": "string",
       "location_name": "string",
       "latitude": "float",
       "longitude": "float"
     }
     ```
   - **Response**:
     - **Success**: 
       ```json
       {
         "message": "Favorite added successfully."
       }
       ```
     - **Failure**:
       ```json
       {
         "message": "Failed to add favorite: error_message"
       }
       ```

### 2. **Retrieve Favorite Locations**
   - **Route**: `/api/favorites`
   - **Method**: `GET`
   - **Purpose**: Retrieves a list of the favorite locations for the currently authenticated user.
   - **Request Parameters**:
     - `user_id` (query parameter)
   - **Response**:
     - **Success**:
       ```json
       [
         {
           "location_name": "City Name",
           "latitude": "float",
           "longitude": "float"
         }
       ]
       ```
     - **Failure**:
       ```json
       {
         "message": "No favorites found."
       }
       ```

### 3. **View Favorite Locations with Weather**
   - **Route**: `/api/favorites/weather`
   - **Method**: `GET`
   - **Purpose**: Displays all favorite locations with their current weather by querying the OpenWeather API.
   - **Request Parameters**:
     - `user_id` (query parameter)
   - **Response**:
     - **Success**:
       ```json
       [
         {
           "location_name": "City Name",
           "temperature": "float",
           "humidity": "float",
           "wind_speed": "float",
           "condition": "weather_condition"
         }
       ]
       ```
     - **Failure**:
       ```json
       {
         "message": "No favorites found."
       }
       ```

### 4. **Simple List of Favorite Locations**
   - **Route**: `/api/favorites/list`
   - **Method**: `GET`
   - **Purpose**: Allows users to view a simple list of all their saved favorite locations.
   - **Request Parameters**:
     - `user_id` (query parameter)
   - **Response**:
     - **Success**:
       ```json
       [
         {
           "location_name": "City Name",
           "latitude": "float",
           "longitude": "float"
         }
       ]
       ```
     - **Failure**:
       ```json
       {
         "message": "No favorites found."
       }
       ```

### 5. **Retrieve Historical Weather Data**
   - **Route**: `/api/weather/historical`
   - **Method**: `GET`
   - **Purpose**: Retrieves historical weather data for a favorite location.
   - **Request Parameters**:
     - `location_name` (query parameter)
     - `user_id` (query parameter)
   - **Response**:
     - **Success**:
       ```json
       [
         {
           "temperature": "float",
           "humidity": "float",
           "wind_speed": "float",
           "condition": "weather_condition",
           "date": "date_string"
         }
       ]
       ```
     - **Failure**:
       ```json
       {
         "message": "No historical data found for this location."
       }
       ```

### 6. **Weather Forecast**
   - **Route**: `/api/weather/forecast`
   - **Method**: `GET`
   - **Purpose**: Retrieves a weather forecast for a favorite location.
   - **Request Parameters**:
     - `location_name` (query parameter)
     - `user_id` (query parameter)
   - **Response**:
     - **Success**:
       ```json
       [
         {
           "date": "date_string",
           "temperature": "float",
           "humidity": "float",
           "wind_speed": "float",
           "condition": "weather_condition"
         }
       ]
       ```
     - **Failure**:
       ```json
       {
         "message": "Failed to fetch forecast data."
       }
       ```

### 7. **Current Weather**
   - **Route**: `/api/weather/current`
   - **Method**: `GET`
   - **Purpose**: Retrieves the current weather data for a specified favorite location and stores it in the database.
   - **Request Parameters**:
     - `location_name` (query parameter)
     - `user_id` (query parameter)
   - **Response**:
     - **Success**:
       ```json
       {
         "location": "City Name",
         "temperature": "float",
         "humidity": "float",
         "wind_speed": "float",
         "condition": "weather_condition"
       }
       ```
     - **Failure**:
       ```json
       {
         "message": "Location is not a favorite."
       }
       ```

---

## Notes:
- **Authentication**: All routes require the user to be authenticated via Flask-Login (`@login_required`).
- **Error Handling**: Errors are returned with descriptive messages and appropriate status codes.
- **Third-Party API**: Weather data is fetched using the OpenWeatherMap API (make sure to replace `API_KEY` with your actual key).

### Example: Add a New Favorite Location
- **Route**: `/api/favorites/add`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
      "user_id": 1,
      "location_name": "San Francisco",
      "latitude": 37.7749,
      "longitude": -122.4194
  }