import unittest
from flask import json
from config import create_app, db
from models import Expense, Category
import datetime

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

    def test_get_expenses(self):
        """Test the GET /expenses endpoint."""
        response = self.client.get("/expense/expenses")
        self.assertEqual(response.status_code, 200)
        self.assertIn("expenses", response.json)

    def test_create_expense(self):
        """Test the POST /create_expense endpoint."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        payload = {
            "Date": "2025-05-14",
            "Category": category_id,
            "Amount": 20.5,
            "Description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("Expense created", response.json["message"])

    def test_create_expense_invalid_date(self):
        """Test POST /create_expense with an invalid date."""
        payload = {
            "Date": "invalid-date",
            "Category": "Food",
            "Amount": 20.5,
            "Description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date format", response.json["error"])

    def test_create_expense_missing_date(self):
        """Test POST /create_expense with a missing date."""
        payload = {
            "Amount": 20.5,
            "Category": "Dining",
            "Description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a date", response.json["message"])

    def test_create_expense_missing_category(self):
        """Test POST /create_expense with a missing category."""
        payload = {
            "Date": "2025-05-14",
            "Amount": 20.5,
            "Description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a category", response.json["message"])

    def test_create_expense_missing_amount(self):
        """Test POST /create_expense with a missing amount."""
        payload = {
            "Date": "2025-05-14",
            "Category": "Dining",
            "Description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include an amount", response.json["message"])

    def test_create_expense_missing_description(self):
        """Test POST /create_expense with a missing category."""
        payload = {
            "Date": "2025-05-14",
            "Category": "Dining",
            "Amount": 20.5,
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a description", response.json["message"])

    def test_update_expense(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint."""
        # First, create an expense
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        # Update the expense
        payload = {"Description": "Dinner"}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        #TODO: add test for when date is changed
        #TODO: add test for when category is changed
        #TODO: add test for when amount is changed

    def test_update_expense_invalid_id(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint with an invalid expense_id."""
        # First, create an expense
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        # Update the expense
        payload = {"Category": "Restaurants"}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id + 1}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Expense not found", response.json["message"])

    def test_delete_expense(self):
        """Test the DELETE /delete_expense/<int:expense_id> endpoint."""
        # First, create an expense
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        # Delete the expense
        response = self.client.delete(f"/expense/delete_expense/{expense_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} deleted", response.json["message"])

    def test_delete_expense_invalid_id(self):
        """Test the DELETE /delete_expense/<int:expense_id> endpoint with invalid expense_id."""
        # First, create an expense
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        # Delete the expense
        response = self.client.delete(f"/expense/delete_expense/{expense_id + 1}")
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Expense not found", response.json["message"])

if __name__ == "__main__":
    unittest.main()