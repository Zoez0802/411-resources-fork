import os
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from weather.config import ProductionConfig
from weather.extensions import db
from weather.models.weather import WeatherModel
from weather.models.user_model import Users
from weather.utils.logger import configure_logger

load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    configure_logger(app.logger)

    # Load configuration
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)

    # Instantiate weather model
    weather_model = WeatherModel()

    ####################################################
    # Healthcheck
    ####################################################

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)

    ####################################################
    # User Management
    ####################################################

    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while creating user",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in successfully"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred during login",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """Log out the current user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out successfully"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

    @app.route("/api/favorites/add", methods=["POST"])
    @login_required
    def add_favorite():
        data = request.get_json()
        user_id = data.get("user_id")
        location_name = data.get("location_name")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        # Check if favorite already exists
        existing_fav = Favorites.query.filter_by(user_id=user_id, location_name=location_name).first()
        if existing_fav:
            return jsonify({"message": "Favorite already exists."}), 409

        # Add favorite location to database
        fav = Favorites(user_id=user_id, location_name=location_name, latitude=latitude, longitude=longitude)
        db.session.add(fav)
        try:
            db.session.commit()
            return jsonify({"message": "Favorite added successfully."}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 500
        
    ############################################################
    #
    # Weather Forecast
    #
    ############################################################

    @app.route("/api/favorites", methods=["GET"])
    @login_required
    def get_favorites():
        """
        Retrieves a list of favorite locations for the currently authenticated user.

        This endpoint queries the database for all favorite locations associated with
        the provided `user_id`. The response includes the name, latitude, and longitude
        of each favorite location.

        Returns:
            json: A JSON array containing the favorite locations, or a message indicating
                no favorites are found.
        """
        user_id = request.args.get("user_id")
        favorites = Favorites.query.filter_by(user_id=user_id).all()

        if not favorites:
            return jsonify({"message": "No favorites found."}), 404

        return jsonify([{
            "location_name": fav.location_name,
            "latitude": fav.latitude,
            "longitude": fav.longitude
        } for fav in favorites])
    
    @app.route("/api/favorites/weather", methods=["GET"])
    @login_required
    def view_all_favorites_with_weather():
        """
        Displays a list of all favorite locations with their current weather.
        """
        user_id = request.args.get("user_id")
        favorites = Favorites.query.filter_by(user_id=user_id).all()

        if not favorites:
            return jsonify({"message": "No favorites found."}), 404

        # Get current weather for each favorite location
        favorite_weather = []
        for fav in favorites:
            location_name = fav.location_name
            # Fetch weather from OpenWeather API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location_name}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()

            if response.status_code != 200:
                favorite_weather.append({"location_name": location_name, "message": "Failed to fetch weather data"})
                continue

            # Extract weather data
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            condition = data["weather"][0]["description"]

            favorite_weather.append({
                "location_name": location_name,
                "temperature": temperature,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "condition": condition
            })

    @app.route("/api/favorites/list", methods=["GET"])
    @login_required
    def get_favorites_list():
        """
        Allows users to view a simple list of all their saved favorite locations.
        """
        user_id = request.args.get("user_id")
        favorites = Favorites.query.filter_by(user_id=user_id).all()

        if not favorites:
            return jsonify({"message": "No favorites found."}), 404

        # List all favorite locations
        favorite_list = [{"location_name": fav.location_name, "latitude": fav.latitude, "longitude": fav.longitude} for fav in favorites]

        return jsonify(favorite_list)
    
    @app.route("/api/weather/historical", methods=["GET"])
    @login_required
    def get_historical_weather():
        """
        Retrieves historical weather data for a favorite location.
        """
        location_name = request.args.get("location_name")
        user_id = request.args.get("user_id")
        # Assuming you store historical data in the database (e.g., in the CurrentWeather model)
        historical_weather = CurrentWeather.query.filter_by(location_name=location_name, user_id=user_id).all()

        if not historical_weather:
            return jsonify({"message": "No historical data found for this location."}), 404

        # Format and return historical weather data
        return jsonify([{
            "temperature": record.temperature,
            "humidity": record.humidity,
            "wind_speed": record.wind_speed,
            "condition": record.condition,
            "date": record.date  # Assuming you store the date
        } for record in historical_weather])
    
    @app.route("/api/weather/forecast", methods=["GET"])
    @login_required
    def get_weather_forecast():
        """
        Retrieves a weather forecast for a favorite location.
        """
        location_name = request.args.get("location_name")
        user_id = request.args.get("user_id")

        # Fetch forecast from the OpenWeather API
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={location_name}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"message": "Failed to fetch forecast data."}), 500

        forecast_data = []
        for forecast in data["list"]:
            forecast_data.append({
                "date": forecast["dt_txt"],
                "temperature": forecast["main"]["temp"],
                "humidity": forecast["main"]["humidity"],
                "wind_speed": forecast["wind"]["speed"],
                "condition": forecast["weather"][0]["description"]
            })

        return jsonify(forecast_data)

    @app.route("/api/weather/current", methods=["GET"])
    @login_required
    def get_current_weather():
        """
        Retrieves the current weather data for a specified favorite location.

        This endpoint fetches the current weather details for the given location using
        the OpenWeatherMap API. It returns temperature, humidity, wind speed, and general
        weather conditions. If the location is a favorite of the user, the weather data
        is stored in the database for future reference.

        Parameters:
            location_name (str): The name of the location to fetch the weather for.
            user_id (str): The ID of the currently authenticated user.

        Returns:
            json: A JSON object containing weather data (temperature, humidity, wind speed,
                condition) or an error message if the location is not a favorite.
        """
        location_name = request.args.get("location_name")
        user_id = request.args.get("user_id")

        # Fetch current weather from the OpenWeather API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location_name}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"message": "Failed to fetch weather data."}), 500

        # Extract data from the API response
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        condition = data["weather"][0]["description"]

        # Check if the location exists in favorites and associate weather data
        favorite = Favorites.query.filter_by(user_id=user_id, location_name=location_name).first()

        if favorite:
            # Save the current weather data to the database
            current_weather = CurrentWeather(
                favorite_id=favorite.id,
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
                condition=condition
            )
            db.session.add(current_weather)
            db.session.commit()

            return jsonify({
                "location": location_name,
                "temperature": temperature,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "condition": condition
            })

        return jsonify({"message": "Location is not a favorite."}), 40
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
