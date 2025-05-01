import pytest
from weather_dashboard.models.favorites_model import WeatherModel

@pytest.fixture
def model():
    """Provide a fresh WeatherModel instance for each test case."""
    return WeatherModel()

#Test add favourite 

def test_add_one_favorite(model):
    """Test adding one favorite location for a user."""
    model.add_favorite("user1", "London")
    assert model.get_favorites("user1") == ["London"]

def test_add_duplicate_favorite(model):
    """Test that adding the same location twice does not duplicate it."""
    model.add_favorite("user1", "London")
    model.add_favorite("user1", "London")
    assert model.get_favorites("user1") == ["London"]

def test_add_multiple_favorites(model):
    """Test adding multiple different favorite locations for the same user."""
    model.add_favorite("user1", "London")
    model.add_favorite("user1", "Tokyo")
    model.add_favorite("user1", "Berlin")
    assert set(model.get_favorites("user1")) == {"London", "Tokyo", "Berlin"}

def test_add_favorites_different_users(model):
    """Test that favorites are tracked separately per user."""
    model.add_favorite("user1", "London")
    model.add_favorite("user2", "Madrid")
    assert model.get_favorites("user1") == ["London"]
    assert model.get_favorites("user2") == ["Madrid"]

#Test Get Favorites 

def test_get_favorites_empty_user(model):
    """Test that an unknown user returns an empty favorite list."""
    assert model.get_favorites("ghost_user") == []

#Test Remove Favorite 

def test_remove_favorite(model):
    """Test removing a location from the user's favorite list."""
    model.add_favorite("user1", "London")
    model.remove_favorite("user1", "London")
    assert model.get_favorites("user1") == []

def test_remove_nonexistent_favorite(model):
    """Test removing a location not in the list does not affect existing favorites."""
    model.add_favorite("user1", "London")
    model.remove_favorite("user1", "Rome")
    assert model.get_favorites("user1") == ["London"]

def test_remove_favorite_from_nonexistent_user(model):
    """Test removing a favorite from a non-existent user does nothing."""
    model.remove_favorite("ghost_user", "Paris")
    assert model.get_favorites("ghost_user") == []

#Test Clear All 

def test_clear_all_favorites(model):
    """Test clearing all favorites for a user removes all entries."""
    model.add_favorite("user1", "London")
    model.add_favorite("user1", "Rome")
    model.clear_all("user1")
    assert model.get_favorites("user1") == []

def test_clear_all_nonexistent_user(model):
    """Test clearing favorites for a user that doesn't exist has no effect."""
    model.clear_all("ghost_user")
    assert model.get_favorites("ghost_user") == []
