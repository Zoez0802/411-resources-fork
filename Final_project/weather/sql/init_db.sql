-- Drop tables if they already exist
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS current_weather;
DROP TABLE IF EXISTS historical_weather;
DROP TABLE IF EXISTS forecast;

-- Table to store user favorite locations
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    location_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    UNIQUE(user_id, location_name)
);

CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_location ON favorites(location_name);

-- Table to store current weather data for favorite locations
CREATE TABLE current_weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    favorite_id INTEGER NOT NULL,
    temperature REAL NOT NULL,
    humidity INTEGER NOT NULL,
    wind_speed REAL NOT NULL,
    condition TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(favorite_id) REFERENCES favorites(id)
);

CREATE INDEX idx_current_weather_fav ON current_weather(favorite_id);
CREATE INDEX idx_current_weather_time ON current_weather(timestamp);

-- Table to store historical weather data
CREATE TABLE historical_weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    favorite_id INTEGER NOT NULL,
    date DATE NOT NULL,
    temperature REAL NOT NULL,
    humidity INTEGER NOT NULL,
    wind_speed REAL NOT NULL,
    condition TEXT NOT NULL,
    FOREIGN KEY(favorite_id) REFERENCES favorites(id),
    UNIQUE(favorite_id, date)
);

CREATE INDEX idx_historical_weather_fav_date ON historical_weather(favorite_id, date);

-- Table to store forecast data for a favorite location
CREATE TABLE forecast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    favorite_id INTEGER NOT NULL,
    forecast_date DATE NOT NULL,
    temp_min REAL NOT NULL,
    temp_max REAL NOT NULL,
    precipitation_chance REAL NOT NULL,
    condition TEXT NOT NULL,
    FOREIGN KEY(favorite_id) REFERENCES favorites(id),
    UNIQUE(favorite_id, forecast_date)
);

CREATE INDEX idx_forecast_fav_date ON forecast(favorite_id, forecast_date);
