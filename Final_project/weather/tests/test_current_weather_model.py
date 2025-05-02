# tests/weather/test_current_weather_model.py

def test_add_and_get_current_weather(model):
    """
    Test adding current weather data for a specific location and retrieving it.
    Verifies that all the values match the input.
    """
    model.add_current_weather("London", temperature=22.5, humidity=55, condition="Sunny")
    result = model.get_current_weather("London")
    assert result is not None
    assert result["location_name"] == "London"
    assert result["temperature"] == 22.5
    assert result["humidity"] == 55
    assert result["condition"] == "Sunny"

def test_get_weather_nonexistent_location(model):
    """
    Test retrieving weather data for a location that does not exist in the database.
    Should return None.
    """
    result = model.get_current_weather("Atlantis")
    assert result is None

def test_overwrite_existing_weather(model):
    """
    Test that adding weather data for the same location overwrites previous data.
    Verifies that only the most recent weather data is stored.
    """
    model.add_current_weather("Tokyo", temperature=18.0, humidity=70, condition="Rain")
    model.add_current_weather("Tokyo", temperature=20.0, humidity=60, condition="Cloudy")
    result = model.get_current_weather("Tokyo")
    assert result["temperature"] == 20.0
    assert result["humidity"] == 60
    assert result["condition"] == "Cloudy"
