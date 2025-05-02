# tests/conftest.py
import pytest
from flask import Flask
from Final_project.weather.models.weather_model import db, WeatherModel

@pytest.fixture(scope="module")
def test_app():
    """
    Create and configure a new Flask app instance with an in-memory SQLite database.
    """
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def model(test_app):
    """
    Provides a fresh WeatherModel instance and resets the DB state.
    """
    with test_app.app_context():
        db.session.query(WeatherModel.FavoriteLocation).delete()
        db.session.commit()
        return WeatherModel()