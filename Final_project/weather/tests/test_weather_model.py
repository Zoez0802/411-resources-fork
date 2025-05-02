import pytest
from Final_project.weather.models.weather_model import WeatherModel, db, FavoriteLocation
from flask import Flask

# ---- Setup Test App and Database ----

@pytest.fixture(scope="module")
def test_app():
    """
    Create and configure a new Flask app instance with an in-memory SQLite database.
    This fixture is scoped to the module and ensures database setup and teardown for all tests.
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
    Provides a fresh WeatherModel instance and a clean state of the FavoriteLocation table before each test.
    """
    with test_app.app_context():
        db.session.query(FavoriteLocation).delete()
        db.session.commit()
        return WeatherModel()

# ---- Test Cases ----

def test_add_one_favorite(model):
    """
    Test adding a single favorite location for a user and verify it exists.
    """
    model.add_favorite(user_id=1, location_name="London", latitude=51.5074, longitude=-0.1278)
    favorites = model.get_favorites(1)
    assert len(favorites) == 1
    assert favorites[0]["location_name"] == "London"

def test_add_duplicate_favorite(model):
    """
    Test adding the same favorite location twice for a user.
    Verifies both entries are added since duplicate prevention is not enforced.
    """
    model.add_favorite(user_id=1, location_name="London", latitude=51.5074, longitude=-0.1278)
    model.add_favorite(user_id=1, location_name="London", latitude=51.5074, longitude=-0.1278)
    favorites = model.get_favorites(1)
    assert len(favorites) == 2  # No unique constraint on duplicates

def test_add_multiple_favorites(model):
    """
    Test adding multiple distinct favorite locations for a single user.
    Verifies all locations are correctly stored.
    """
    model.add_favorite(1, "London", 51.5074, -0.1278)
    model.add_favorite(1, "Tokyo", 35.6895, 139.6917)
    model.add_favorite(1, "Berlin", 52.5200, 13.4050)
    favorites = model.get_favorites(1)
    names = [fav["location_name"] for fav in favorites]
    assert set(names) == {"London", "Tokyo", "Berlin"}

def test_add_favorites_different_users(model):
    """
    Test that favorite locations added by different users do not conflict.
    """
    model.add_favorite(1, "London", 51.5074, -0.1278)
    model.add_favorite(2, "Madrid", 40.4168, -3.7038)
    favs_user1 = model.get_favorites(1)
    favs_user2 = model.get_favorites(2)
    assert favs_user1[0]["location_name"] == "London"
    assert favs_user2[0]["location_name"] == "Madrid"

def test_get_favorites_empty_user(model):
    """
    Test retrieving favorite locations for a user that has none.
    Should return an empty list.
    """
    assert model.get_favorites(999) == []

def test_remove_favorite(model):
    """
    Test removing a favorite location and verifying it no longer exists.
    """
    model.add_favorite(1, "Rome", 41.9028, 12.4964)
    model.remove_favorite(1, "Rome")
    favorites = model.get_favorites(1)
    assert all(fav["location_name"] != "Rome" for fav in favorites)

def test_remove_nonexistent_favorite(model):
    """
    Test attempting to remove a location that doesn't exist.
    Ensures it does not affect existing data.
    """
    model.add_favorite(1, "London", 51.5074, -0.1278)
    model.remove_favorite(1, "Nonexistent City")
    favorites = model.get_favorites(1)
    assert any(fav["location_name"] == "London" for fav in favorites)

def test_remove_favorite_from_nonexistent_user(model):
    """
    Test removing a favorite from a user that doesn't exist.
    Ensures no error is thrown and data remains unchanged.
    """
    model.remove_favorite(999, "Paris")  # should not throw
    assert model.get_favorites(999) == []

def test_clear_all_by_manual_delete(model):
    """
    Simulate clearing all favorites for a user via direct database query (since no method exists).
    """
    model.add_favorite(1, "Paris", 48.8566, 2.3522)
    model.add_favorite(1, "Berlin", 52.5200, 13.4050)
    db.session.query(FavoriteLocation).filter_by(user_id=1).delete()
    db.session.commit()
    assert model.get_favorites(1) == []