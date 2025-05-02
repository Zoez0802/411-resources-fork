import logging
from datetime import datetime
from typing import List

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

logger = logging.getLogger(__name__)

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
