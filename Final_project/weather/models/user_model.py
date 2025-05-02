import hashlib
import logging
import os

from flask_login import UserMixin
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Column, Integer, String

from weather.db import db
from weather.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(64), nullable=False)  # SHA-256 hash = 64 hex chars
    salt = Column(String(32), nullable=False)      # 16 bytes salt = 32 hex chars

    @staticmethod
    def _generate_hashed_password(password: str) -> tuple[str, str]:
        """Generates a salted, hashed password."""
        salt = os.urandom(16).hex()
        hashed_pw = hashlib.sha256((salt + password).encode()).hexdigest()
        return salt, hashed_pw

    @classmethod
    def create_user(cls, username: str, password: str) -> None:
        """Create a new user with a salted, hashed password."""
        if db.session.query(cls).filter_by(username=username).first():
            logger.error("Duplicate username: %s", username)
            raise ValueError(f"User with username '{username}' already exists")
        try:
            salt, hashed_pw = cls._generate_hashed_password(password)
            user = cls(username=username, password=hashed_pw, salt=salt)
            db.session.add(user)
            db.session.commit()
            logger.info("User successfully added to the database: %s", username)
        except Exception as e:
            logger.error("Database error: %s", str(e))
            db.session.rollback()
            raise

    @classmethod
    def check_password(cls, username: str, password: str) -> bool:
        """Check if a given password matches the stored password for a user."""
        user = db.session.query(cls).filter_by(username=username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        hashed_input = hashlib.sha256((user.salt + password).encode()).hexdigest()
        return hashed_input == user.password

    @classmethod
    def delete_user(cls, username: str) -> None:
        """Delete a user from the database."""
        user = db.session.query(cls).filter_by(username=username).first()
        if not user:
            logger.info("User %s not found", username)
            raise ValueError(f"User {username} not found")
        db.session.delete(user)
        db.session.commit()
        logger.info("User %s deleted successfully", username)

    def get_id(self) -> str:
        """Get the ID of the user."""
        return str(self.id)

    @classmethod
    def get_id_by_username(cls, username: str) -> int:
        """Retrieve the ID of a user by username."""
        user = db.session.query(cls).filter_by(username=username).first()
        if not user:
            raise ValueError(f"User {username} not found")
        return user.id

    @classmethod
    def update_password(cls, username: str, new_password: str) -> None:
        """Update the password for a user."""
        user = db.session.query(cls).filter_by(username=username).first()
        if not user:
            logger.info("User %s not found", username)
            raise ValueError(f"User {username} not found")
        new_salt, new_hashed_pw = cls._generate_hashed_password(new_password)
        user.password = new_hashed_pw
        user.salt = new_salt
        db.session.commit()
        logger.info("Password updated successfully for user: %s", username)