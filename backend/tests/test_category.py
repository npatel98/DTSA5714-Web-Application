import unittest
from flask import json
from config import create_app, db
from models import Category

class ExpenseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize the database."""
        self.app = create_app()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_categories_empty(self):
        """Test the GET /categories endpoint on an empty table."""
        response = self.client.get("/category/categories")
        self.assertEqual(response.status_code, 200)
        self.assertIn("expenses", response.json)

    def test_get_category_populated(self):
        """Test the GET /categories endpoint on a populated table."""
        with self.app.app_context():
            category1 = Category(category="Restaurants")
            category2 = Category(category="Groceries")
            category3 = Category(category="Shopping")
            db.session.add(category1)
            db.session.add(category2)
            db.session.add(category3)
            db.session.commit()

    def test_create_category(self):
        """Test the POST /create_category endpoint."""
        payload = {
            "Category": "Dining"
        }
        response = self.client.post(
            "/category/create_category", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("Category created", response.json["message"])

    def test_update_category(self):
        """Test the PATCH /update_category/<int:category_id> endpoint."""
        # First, create a category
        with self.app.app_context():
            category = Category(category="Dining")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        # Update the category
        payload = {"Category": "Restaurants"}
        response = self.client.patch(
            f"/category/update_category/{category_id}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Category {category_id} updated", response.json["message"])

    def test_update_category_invalid_id(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint with an invalid category_id."""
        # First, create a category
        with self.app.app_context():
            category = Category(category="Dining")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        # Update the category
        payload = {"Category": "Restaurants"}
        response = self.client.patch(
            f"/category/update_category/{category_id + 1}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Category not found", response.json["message"])

    def test_delete_category(self):
        """Test the DELETE /delete_category/<int:category_id> endpoint."""
        # First, create a category
        with self.app.app_context():
            category = Category(category="Dining")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        # Delete the category
        response = self.client.delete(f"/category/delete_category/{category_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Category {category_id} deleted", response.json["message"])

    def test_delete_expense_invalid_id(self):
        """Test the DELETE /delete_category/<int:category_id> endpoint with invalid category_id."""
        # First, create a category
        with self.app.app_context():
            category = Category(category="Dining")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        # Delete the category
        response = self.client.delete(f"/category/delete_category/{category_id + 1}")
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Category not found", response.json["message"])


if __name__ == "__main__":
    unittest.main()