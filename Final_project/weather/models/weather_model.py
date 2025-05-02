import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy

from weather.db import db
from weather.models import FavoriteLocation, CurrentWeather  # Assuming these exist

logger = logging.getLogger(__name__)

class WeatherModel:
    """
    WeatherModel handles favorite locations and associated weather data for users.
    """

    @staticmethod
    def add_favorite(user_id: int, location_name: str, latitude: float, longitude: float) -> None:
        try:
            favorite = FavoriteLocation(
                user_id=user_id,
                location_name=location_name,
                latitude=latitude,
                longitude=longitude
            )
            db.session.add(favorite)
            db.session.commit()
            logger.info("Added favorite location '%s' for user %d", location_name, user_id)
        except IntegrityError:
            db.session.rollback()
            logger.error("Favorite location '%s' already exists for user %d", location_name, user_id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error adding favorite location: %s", str(e))

    @staticmethod
    def remove_favorite(user_id: int, location_name: str) -> None:
        favorite = FavoriteLocation.query.filter_by(user_id=user_id, location_name=location_name).first()
        if not favorite:
            logger.warning("Favorite location '%s' not found for user %d", location_name, user_id)
            return

        try:
            db.session.delete(favorite)
            db.session.commit()
            logger.info("Removed favorite location '%s' for user %d", location_name, user_id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error removing favorite location: %s", str(e))

    @staticmethod
    def get_favorites(user_id: int) -> List[dict]:
        try:
            favorites = FavoriteLocation.query.filter_by(user_id=user_id).all()
            return [fav.to_dict() for fav in favorites]
        except Exception as e:
            logger.error("Error retrieving favorites for user %d: %s", user_id, str(e))
            return []

    @staticmethod
    def add_current_weather(
        favorite_location_id: int,
        temperature: float,
        humidity: float,
        wind_speed: float,
        condition: str
    ) -> None:
        try:
            weather = CurrentWeather(
                favorite_location_id=favorite_location_id,
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                condition=condition,
                date=datetime.utcnow()
            )
            db.session.add(weather)
            db.session.commit()
            logger.info("Added current weather for favorite location ID %d", favorite_location_id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error adding current weather: %s", str(e))

    @staticmethod
    def get_current_weather(user_id: int, location_name: str) -> dict:
        try:
            favorite = FavoriteLocation.query.filter_by(user_id=user_id, location_name=location_name).first()
            if not favorite:
                return {"message": "Location not found in favorites."}

            current = CurrentWeather.query \
                .filter_by(favorite_location_id=favorite.id) \
                .order_by(CurrentWeather.date.desc()) \
                .first()

            return current.to_dict() if current else {"message": "No current weather data available."}
        except Exception as e:
            logger.error("Error retrieving current weather: %s", str(e))
            return {"message": "Internal error retrieving weather."}