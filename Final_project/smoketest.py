import unittest
from flask import json
from weather.app import create_app, db
from weather.models.user_model import Users
from weather.models.favorite_model import Favorites

class SmokeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()

        self.username = "smoketest"
        self.password = "password123"
        self.location = {
            "location_name": "Boston",
            "latitude": 42.3601,
            "longitude": -71.0589
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_full_flow(self):
        # Healthcheck
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Service is running", r.get_data(as_text=True))

        # Create user
        r = self.client.put("/api/create-user", json={
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(r.status_code, 201)

        # Login
        r = self.client.post("/api/login", json={
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(r.status_code, 200)
        cookie = r.headers.get("Set-Cookie")

        # Add favorite
        r = self.client.post("/api/favorites/add", json={
            "user_id": self.username,
            **self.location
        }, headers={"Cookie": cookie})
        self.assertIn(r.status_code, [201, 409])

        # Get favorites
        r = self.client.get("/api/favorites", query_string={
            "user_id": self.username
        }, headers={"Cookie": cookie})
        self.assertIn(r.status_code, [200, 404])

        # Logout
        r = self.client.post("/api/logout", headers={"Cookie": cookie})
        self.assertEqual(r.status_code, 200)

if __name__ == "__main__":
    unittest.main()