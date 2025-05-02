import logging
from datetime import datetime
from typing import List

from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

logger = logging.getLogger(__name__)

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
