from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Returns a simple status message to verify the app is running."""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True)
