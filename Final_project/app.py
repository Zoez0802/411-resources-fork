from flask import Flask, jsonify, request, session
from models.favorites_model import WeatherModel

app = Flask(__name__)
app.secret_key = 'dev'  

weather_model = WeatherModel()

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Returns a simple status message to verify the app is running."""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True)
