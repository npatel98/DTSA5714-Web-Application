import unittest
from flask import json
from config import create_app, db
from models import Expense, Category
import datetime

class ExpenseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize the database."""
        self.app = create_app('testing')
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up the database after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_expenses_empty(self):
        """Test the GET /expenses endpoint on an empty table."""
        response = self.client.get("/expense/expenses")
        self.assertEqual(response.status_code, 200)
        self.assertIn("expenses", response.json)

    def test_get_expenses_populated(self):
        """Test the GET /expenses endpoint on a populated table."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense1 = Expense(date=datetime.date(2022, 3, 24), category_id=category_id, amount=15.3, description="Breakfast")
            expense2 = Expense(date=datetime.date(2023, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            expense3 = Expense(date=datetime.date(2025, 1, 12), category_id=category_id, amount=60.54, description="Dinner")
            db.session.add(expense1)
            db.session.add(expense2)
            db.session.add(expense3)
            db.session.commit()

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
            "date": "2025-05-14",
            "categoryId": category_id,
            "amount": 20.5,
            "description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 201, response.json["message"])
        self.assertIn("Expense created", response.json["message"])

    def test_create_expense_invalid_date(self):
        """Test POST /create_expense with an invalid date."""
        payload = {
            "date": "invalid-date",
            "categoryId": 2,
            "amount": 20.5,
            "description": "Lunch"
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
            "date": "2025-05-14",
            "amount": 20.5,
            "description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a category", response.json["message"])

    def test_create_expense_missing_amount(self):
        """Test POST /create_expense with a missing amount."""
        payload = {
            "date": "2025-05-14",
            "categoryId": 2,
            "description": "Lunch"
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include an amount", response.json["message"])

    def test_create_expense_missing_description(self):
        """Test POST /create_expense with a missing category."""
        payload = {
            "date": "2025-05-14",
            "categoryId": 2,
            "amount": 20.5,
        }
        response = self.client.post(
            "/expense/create_expense", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a description", response.json["message"])

    def test_update_expense_date(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint to change date."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"date": "2025-04-03"}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        updated_expense = Expense.query.get(expense_id)
        self.assertEqual(updated_expense.date, datetime.date(2025, 4, 3))

    def test_update_expense_invalid_date(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint fails with invalid date."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"date": 1}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date format. Use YYYY-MM-DD.", response.json["error"])


    def test_update_expense_category(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint to change category."""
        with self.app.app_context():
            old_category = Category(category="Dining")
            db.session.add(old_category)
            db.session.commit()
            old_category_id = old_category.id

            new_category = Category(category="Restaurants")
            db.session.add(new_category)
            db.session.commit()
            new_category_id = new_category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=old_category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        self.assertEqual(expense.category_id, old_category_id)
        payload = {"categoryId": new_category_id}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id}", data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        updated_expense = Expense.query.get(expense_id)
        self.assertEqual(updated_expense.category_id, new_category_id)
        
    def test_update_expense_invalid_category(self):
        pass

    def test_update_expense_amount(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint to change amount."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id
            
        payload = {"amount": 100.82}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        updated_expense = Expense.query.get(expense_id)
        self.assertEqual(updated_expense.amount, 100.82)

    def test_update_expense_invalid_amount(self):
        pass
    
    def test_update_expense_description(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint to change description."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"description": "Dinner"}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        updated_expense = Expense.query.get(expense_id)
        self.assertEqual(updated_expense.description, "Dinner")

    def test_update_expense_invalid_description(self):
        pass

    def test_update_expense_invalid_id(self):
        """Test the PATCH /update_expense/<int:expense_id> endpoint with an invalid expense_id."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"categoryId": 2}
        response = self.client.patch(
            f"/expense/update_expense/{expense_id + 1}", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Expense not found", response.json["message"])

    def test_delete_expense(self):
        """Test the DELETE /delete_expense/<int:expense_id> endpoint."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        response = self.client.delete(f"/expense/delete_expense/{expense_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} deleted", response.json["message"])

    def test_delete_expense_invalid_id(self):
        """Test the DELETE /delete_expense/<int:expense_id> endpoint with invalid expense_id."""
        with self.app.app_context():
            category = Category(category="Restaurants")
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(date=datetime.date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        response = self.client.delete(f"/expense/delete_expense/{expense_id + 1}")
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Expense not found", response.json["message"])

if __name__ == "__main__":
    unittest.main()