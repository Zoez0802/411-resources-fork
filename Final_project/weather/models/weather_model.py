import logging
from datetime import datetime
from typing import List

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

logger = logging.getLogger(__name__)

class FavoriteLocation(db.Model):
    """Represents a user's favorite location in the system.
    
    This model maps to the 'favorite_locations' table and stores user favorites.
    It includes location information such as name, latitude, and longitude.
    """
    __tablename__ = 'favorite_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_name = db.Column(db.String(120), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # Define the relationship between users and their favorite locations
    user = db.relationship('User', backref='favorite_locations', lazy=True)

    def __init__(self, user_id: int, location_name: str, latitude: float, longitude: float):
        self.user_id = user_id
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        """Convert the favorite location into a dictionary."""
        return {
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude
        }


class CurrentWeather(db.Model):
    """Represents the current weather for a location stored in the system.

    This model maps to the 'current_weather' table and stores the current weather
    data for each location.
    """
    __tablename__ = 'current_weather'
    
    id = db.Column(db.Integer, primary_key=True)
    favorite_location_id = db.Column(db.Integer, db.ForeignKey('favorite_locations.id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # Define the relationship between weather data and favorite locations
    favorite_location = db.relationship('FavoriteLocation', backref='current_weather', lazy=True)

    def __init__(self, favorite_location_id: int, temperature: float, humidity: float, wind_speed: float, condition: str):
        self.favorite_location_id = favorite_location_id
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.condition = condition

    def to_dict(self):
        """Convert the current weather data into a dictionary."""
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "condition": self.condition,
            "date": self.date.isoformat()
        }

class WeatherModel:
    """The WeatherModel handles favorite locations and weather data.

    This model supports adding, removing, and viewing favorite locations,
    as well as saving and retrieving weather data.
    """

    def add_favorite(self, user_id: int, location_name: str, latitude: float, longitude: float) -> None:
        """Add a favorite location for a user."""
        try:
            favorite = FavoriteLocation(user_id=user_id, location_name=location_name, latitude=latitude, longitude=longitude)
            db.session.add(favorite)
            db.session.commit()
            logger.info(f"Added favorite location '{location_name}' for user {user_id}.")
        except IntegrityError:
            db.session.rollback()
            logger.error(f"Failed to add favorite location '{location_name}' for user {user_id}.")

    def remove_favorite(self, user_id: int, location_name: str) -> None:
        """Remove a favorite location from a user's list."""
        favorite = FavoriteLocation.query.filter_by(user_id=user_id, location_name=location_name).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            logger.info(f"Removed favorite location '{location_name}' for user {user_id}.")
        else:
            logger.warning(f"Favorite location '{location_name}' not found for user {user_id}.")

    def get_favorites(self, user_id: int) -> List[dict]:
        """Get a list of favorite locations for a user."""
        favorites = FavoriteLocation.query.filter_by(user_id=user_id).all()
        return [fav.to_dict() for fav in favorites]

    def add_current_weather(self, favorite_location_id: int, temperature: float, humidity: float, wind_speed: float, condition: str) -> None:
        """Add the current weather data for a favorite location."""
        current_weather = CurrentWeather(
            favorite_location_id=favorite_location_id,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            condition=condition
        )
        db.session.add(current_weather)
        db.session.commit()
        logger.info(f"Added current weather data for favorite location ID {favorite_location_id}.")

    def get_current_weather(self, user_id: int, location_name: str) -> dict:
        """Get current weather for a user's favorite location."""
        favorite = FavoriteLocation.query.filter_by(user_id=user_id, location_name=location_name).first()
        if favorite:
            current_weather = CurrentWeather.query.filter_by(favorite_location_id=favorite.id).order_by(CurrentWeather.date.desc()).first()
            if current_weather:
                return current_weather.to_dict()
            else:
                return {"message": "No current weather data available."}
        return {"message": "Location not found in favorites."}
