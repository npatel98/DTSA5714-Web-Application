import unittest
from flask import json
from config import create_app, db
from dotenv import load_dotenv
from models import User
from werkzeug.security import generate_password_hash
import os
import uuid

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize the database."""
        self.app = create_app('testing')
        self.app.config["TESTING"] = True
        self.app.config['JWT_SECRET_KEY'] = uuid.uuid4().hex
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the database after each test."""
        from config import db
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        """Test the register endpoint."""
        payload = {
            "username": "newuser",
            "password": "newpassword"
        }
        response = self.client.post(
            "/auth/register", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("User registered successfully", response.json["message"])

    def test_login(self):
        """Test the login endpoint."""
        with self.app.app_context():
            # Create a test user
            user = User(username="testuser", password=generate_password_hash("testpassword"))
            db.session.add(user)
            db.session.commit()

        payload = {
            "username": "testuser",
            "password": "testpassword"
        }
        response = self.client.post(
            "/auth/login", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json)
        self.assertIn("refesh_token", response.json)
        self.assertIn("user", response.json)
        self.assertIn("Login successful", response.json["message"])

    def test_login_invalid_username(self):
        """Test the login endpoint with invalid username."""
        with self.app.app_context():
            # Create a test user
            user = User(username="testuser", password="testpassword")
            db.session.add(user)
            db.session.commit()

        payload = {
            "username": "invaliduser",
            "password": "testpassword"
        }
        response = self.client.post(
            "/auth/login", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.json["message"])

    def test_login_invalid_password(self):
        """Test the login endpoint with invalid password."""
        with self.app.app_context():
            # Create a test user
            user = User(username="testuser", password="testpassword")
            db.session.add(user)
            db.session.commit()

        payload = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(
            "/auth/login", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.json["message"])

    def test_logout(self):
        """Test the logout endpoint."""
        with self.app.app_context():
            # Create a test user
            user = User(username="testuser", password="testpassword")
            db.session.add(user)
            db.session.commit()

        payload = {
            "username": "testuser"
        }
        response = self.client.post(
            "/auth/logout", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Logout successful", response.json["message"])

    def test_refresh(self):
        """Test the refresh endpoint."""
        with self.app.app_context():
            user = User(username="testuser", password=generate_password_hash("testpassword"))
            db.session.add(user)
            db.session.commit()

        payload = {
            "username": "testuser",
            "password": "testpassword"
        }
        login_response = self.client.post(
            "/auth/login", data=json.dumps(payload), content_type="application/json"
        )
        refresh_token = login_response.json["refesh_token"]

        headers = {
            "Authorization": f"Bearer {refresh_token}"
        }
        refresh_response = self.client.post("/auth/refresh", headers=headers)
        
        self.assertEqual(refresh_response.status_code, 200)
        self.assertNotEqual(login_response.json["access_token"], refresh_response.json["access_token"])
        self.assertIn("access_token", refresh_response.json)
        self.assertIn("Token refresh successful", refresh_response.json["message"])