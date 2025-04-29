import logging
from typing import Dict, List

## for weather dashboard feature:
## set favourite location


logger = logging.getLogger(__name__)

class WeatherModel:
    """An in-memory model to store each user's favorite locations.
    
    Users can add and save their favorite locations to their profile. This feature 
    simplifies accessing weather data for commonly viewed cities or areas without 
    needing to search for them each time.
    
    """

    def __init__(self):
        """Initialize the WeatherModel with an empty dictionary."""
        self.user_favorites: Dict[str, List[str]] = {}

    def add_favorite(self, username: str, location: str) -> None:
        """Add a favorite location for a user.
        
        Args:
            username (str): The name of the user.
            location (str): The location (city name) to add.
        """
        if username not in self.user_favorites:
            self.user_favorites[username] = []
        if location not in self.user_favorites[username]:
            self.user_favorites[username].append(location)
            logger.info(f"Added favorite '{location}' for user '{username}'.")

    def remove_favorite(self, username: str, location: str) -> None:
        """Remove a favorite location from a user's list.
        
        Args:
            username (str): The name of the user.
            location (str): The location (city name) to remove.
        """
        if username in self.user_favorites and location in self.user_favorites[username]:
            self.user_favorites[username].remove(location)
            logger.info(f"Removed favorite '{location}' for user '{username}'.")

    def get_favorites(self, username: str) -> List[str]:
        """Get the list of favorite locations for a user.
        
        Args:
            username (str): The name of the user.

        Returns:
            List[str]: A list of favorite city names.
        """
        return self.user_favorites.get(username, [])

    def clear_all(self, username: str) -> None:
        """Clear all favorite locations for a user.
        
        Args:
            username (str): The name of the user.
        """
        if username in self.user_favorites:
            del self.user_favorites[username]
            logger.info(f"Cleared all favorites for user '{username}'.")
