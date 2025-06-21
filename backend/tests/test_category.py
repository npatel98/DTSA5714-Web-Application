import unittest
from flask import json
from config import create_app, db
from models import Category, User
from dotenv import load_dotenv
from datetime import datetime, UTC
from flask_jwt_extended import create_access_token
import uuid

class CategoryTestCase(unittest.TestCase):
    def setUp(self):
        load_dotenv('.flaskenv')
        self.app = create_app('testing')
        self.app.config["TESTING"] = True
        self.app.config['JWT_SECRET_KEY'] = uuid.uuid4().hex
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

            self.test_user = User(
                username="test_user",
                password="test_password"
            )
            db.session.add(self.test_user)
            db.session.commit()
            db.session.refresh(self.test_user)
            self.user_id = self.test_user.id
            
            self.access_token = create_access_token(identity=self.user_id)
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_categories_empty(self):
        response = self.client.get(
            f"api/category/{self.user_id}/categories",
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("categories", response.json)

    def test_create_category(self):
        payload = {
            "Category": "Dining"
        }
        response = self.client.post(
            f"api/category/{self.user_id}/categories",
            data=json.dumps(payload),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("Category created", response.json["message"])

    def test_update_category(self):
        with self.app.app_context():
            category = Category(
                category="Dining",
                user_id=self.user_id,
                created_at=datetime.now(tz=UTC),
                updated_at=datetime.now(tz=UTC)
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        payload = {"Category": "Restaurants"}
        response = self.client.patch(
            f"api/category/{self.user_id}/categories/{category_id}",
            data=json.dumps(payload),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Category {category_id} updated", response.json["message"])

        with self.app.app_context():
            upated_category = Category.query.filter_by(user_id=self.user_id, id=category_id).first()
            self.assertEqual(upated_category.category, "Restaurants")

    def test_delete_category(self):
        with self.app.app_context():
            category = Category(
                category="Clothing",
                user_id=self.user_id,
                created_at=datetime.now(tz=UTC),
                updated_at=datetime.now(tz=UTC)
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            response = self.client.delete(
                f"api/category/{self.user_id}/categories/{category_id}",
                headers=self.headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(f"Category {category_id} deleted", response.json["message"])

    def test_wrong_user_access(self):
        with self.app.app_context():
            second_user = User(
                username="test_user_2",
                password="test123"
            )
            db.session.add(second_user)
            db.session.commit()
            db.session.refresh(second_user)


            user_2_access_token = create_access_token(identity=second_user.id)
            user_2_headers = {
                "Authorization": f"Bearer {user_2_access_token}",
                "Content-Type": "application/json"
            }
            
            response = self.client.get(
                f"api/category/{self.user_id}/categories",
                headers=user_2_headers
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn("Unauthorized access", response.json["message"])

    def test_different_users_same_category(self):
        with self.app.app_context():
            second_user = User(
                username="test_user_2",
                password="test123"
            )
            db.session.add(second_user)
            db.session.commit()
            db.session.refresh(second_user)
            
            user_2_access_token = create_access_token(identity=second_user.id)
            user_2_headers = {
                "Authorization": f"Bearer {user_2_access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "Category": "Groceries"
            }

            response1 = self.client.post(
                f"api/category/{self.user_id}/categories",
                data=json.dumps(payload),
                headers=self.headers
            )
            self.assertEqual(response1.status_code, 201)

            response2 = self.client.post(
                f"api/category/{second_user.id}/categories",
                data=json.dumps(payload),
                headers=user_2_headers
            )
            self.assertEqual(response2.status_code, 201)

            user1_category = Category.query.filter_by(user_id=self.user_id, category="Groceries").first()
            user2_category = Category.query.filter_by(user_id=second_user.id, category="Groceries").first()
            
            self.assertIsNotNone(user1_category)
            self.assertIsNotNone(user2_category)
            self.assertNotEqual(user1_category.id, user2_category.id)
        

if __name__ == "__main__":
    unittest.main()