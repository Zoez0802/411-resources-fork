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