# tests/weather/test_favorite_location_model.py

def test_add_one_favorite(model):
    """
    Test adding a single favorite location for a user and verify it exists in the database.
    Ensures the location is correctly added and retrieved.
    """
    model.add_favorite(user_id=1, location_name="London", latitude=51.5074, longitude=-0.1278)
    favorites = model.get_favorites(1)
    assert len(favorites) == 1
    assert favorites[0]["location_name"] == "London"

def test_add_duplicate_favorite(model):
    """
    Test adding the same favorite location twice for a user.
    Verifies that duplicates are allowed and both entries are added.
    """
    model.add_favorite(user_id=1, location_name="London", latitude=51.5074, longitude=-0.1278)
    model.add_favorite(user_id=1, location_name="London", latitude=51.5074, longitude=-0.1278)
    favorites = model.get_favorites(1)
    assert len(favorites) == 2  # Duplicate allowed

def test_add_multiple_favorites(model):
    """
    Test adding multiple distinct favorite locations for a single user.
    Ensures that all locations are correctly stored and can be retrieved.
    """
    model.add_favorite(1, "London", 51.5074, -0.1278)
    model.add_favorite(1, "Tokyo", 35.6895, 139.6917)
    model.add_favorite(1, "Berlin", 52.5200, 13.4050)
    names = [fav["location_name"] for fav in model.get_favorites(1)]
    assert set(names) == {"London", "Tokyo", "Berlin"}

def test_add_favorites_different_users(model):
    """
    Test that favorite locations added by different users do not conflict.
    Ensures that users' favorite locations are isolated.
    """
    model.add_favorite(1, "London", 51.5074, -0.1278)
    model.add_favorite(2, "Madrid", 40.4168, -3.7038)
    assert model.get_favorites(1)[0]["location_name"] == "London"
    assert model.get_favorites(2)[0]["location_name"] == "Madrid"

def test_get_favorites_empty_user(model):
    """
    Test retrieving favorite locations for a user who has no favorites.
    Should return an empty list.
    """
    assert model.get_favorites(999) == []

def test_remove_favorite(model):
    """
    Test removing a favorite location and ensuring it is no longer in the user's favorites.
    Verifies that the location is deleted correctly.
    """
    model.add_favorite(1, "Rome", 41.9028, 12.4964)
    model.remove_favorite(1, "Rome")
    assert all(fav["location_name"] != "Rome" for fav in model.get_favorites(1))

def test_remove_nonexistent_favorite(model):
    """
    Test attempting to remove a favorite location that does not exist.
    Ensures that it does not affect existing favorites.
    """
    model.add_favorite(1, "London", 51.5074, -0.1278)
    model.remove_favorite(1, "Nonexistent City")
    assert any(fav["location_name"] == "London" for fav in model.get_favorites(1))

def test_remove_favorite_from_nonexistent_user(model):
    """
    Test attempting to remove a favorite from a user who doesn't exist.
    Ensures no error is thrown and data remains unchanged.
    """
    model.remove_favorite(999, "Paris")  # Should not throw an error
    assert model.get_favorites(999) == []

def test_clear_all_by_manual_delete(model):
    """
    Test clearing all favorites for a user by directly deleting them from the database.
    Ensures that all the user's favorites are removed.
    """
    model.add_favorite(1, "Paris", 48.8566, 2.3522)
    model.add_favorite(1, "Berlin", 52.5200, 13.4050)
    model.db.session.query(model.FavoriteLocation).filter_by(user_id=1).delete()
    model.db.session.commit()
    assert model.get_favorites(1) == []