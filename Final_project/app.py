from flask import Flask, jsonify, request, session
from models.favorites_model import WeatherModel

app = Flask(__name__)
app.secret_key = 'dev'  

weather_model = WeatherModel()

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Returns a simple status message to verify the app is running."""
    return jsonify({"status": "ok"}), 200
    

@app.route('/favorite', methods=['POST'])
def add_favorite():
    """Adds a favorite location for the logged-in user."""
    # TEMPORARY: hardcode a test user (remove when login is ready)
    username = "test_user"

    data = request.get_json()
    location = data.get("location")

    if not location:
        return jsonify({"error": "Missing location"}), 400

    weather_model.add_favorite(username, location)

    return jsonify({
        "message": f"Added {location} to favorites.",
        "favorites": weather_model.get_favorites(username)
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
