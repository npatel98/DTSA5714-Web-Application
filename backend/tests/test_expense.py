import unittest
from flask import json
from config import create_app, db
from models import Expense, Category, User
from datetime import date, datetime, UTC
from dotenv import load_dotenv
import uuid
from flask_jwt_extended import create_access_token

class ExpenseTestCase(unittest.TestCase):
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

    def test_get_expenses_empty(self):
        response = self.client.get(
            f"/api/expense/{self.user_id}/expenses",
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("expenses", response.json)

    def test_get_expenses_populated(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id,
                created_at=datetime.now(tz=UTC),
                updated_at=datetime.now(tz=UTC)
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense1 = Expense(user_id=self.user_id, date=date(2022, 3, 24), category_id=category_id, amount=15.3, description="Breakfast")
            expense2 = Expense(user_id=self.user_id, date=date(2023, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            expense3 = Expense(user_id=self.user_id, date=date(2025, 1, 12), category_id=category_id, amount=60.54, description="Dinner")
            db.session.add(expense1)
            db.session.add(expense2)
            db.session.add(expense3)
            db.session.commit()

        response = self.client.get(
            f"/api/expense/{self.user_id}/expenses",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("expenses", response.json)

    def test_create_expense(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

        payload = {
            "date": "2025-05-14",
            "categoryId": category_id,
            "amount": 20.5,
            "description": "Lunch",
        }
        response = self.client.post(
            f"/api/expense/{self.user_id}/expenses", 
            data=json.dumps(payload), 
            headers=self.headers
        )

        self.assertEqual(response.status_code, 201, response.json["message"])
        self.assertIn("Expense created", response.json["message"])

    def test_create_expense_invalid_date(self):
        payload = {
            "date": "invalid-date",
            "categoryId": 2,
            "amount": 20.5,
            "description": "Lunch"
        }
        response = self.client.post(
            f"/api/expense/{self.user_id}/expenses", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date format", response.json["error"])

    def test_create_expense_missing_date(self):
        payload = {
            "Amount": 20.5,
            "Category": "Dining",
            "Description": "Lunch"
        }
        response = self.client.post(
            f"/api/expense/{self.user_id}/expenses", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a date", response.json["message"])

    def test_create_expense_missing_category(self):
        payload = {
            "date": "2025-05-14",
            "amount": 20.5,
            "description": "Lunch"
        }
        response = self.client.post(
            f"/api/expense/{self.user_id}/expenses", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a category", response.json["message"])

    def test_create_expense_missing_amount(self):
        payload = {
            "date": "2025-05-14",
            "categoryId": 2,
            "description": "Lunch"
        }
        response = self.client.post(
            f"/api/expense/{self.user_id}/expenses", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include an amount", response.json["message"])

    def test_create_expense_missing_description(self):
        payload = {
            "date": "2025-05-14",
            "categoryId": 2,
            "amount": 20.5,
        }
        response = self.client.post(
            f"/api/expense/{self.user_id}/expenses", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("You must include a description", response.json["message"])

    def test_update_expense_date(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(user_id=self.user_id, date=date(2025, 5, 14), category_id=category_id, amount=20.5, description="Lunch")
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"date": "2025-04-03"}
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        with self.app.app_context():
            updated_expense = Expense.query.filter_by(id=expense_id, user_id=self.user_id).first()
            self.assertEqual(updated_expense.date, date(2025, 4, 3))

    def test_update_expense_invalid_date(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(
                user_id=self.user_id, 
                date=date(2025, 5, 14), 
                category_id=category_id, 
                amount=20.5, 
                description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"date": 1}
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid value for date", response.json["error"])

    def test_update_expense_category(self):
        with self.app.app_context():
            old_category = Category(
                category="Dining",
                user_id=self.user_id,
            )
            db.session.add(old_category)
            db.session.commit()
            old_category_id = old_category.id

            new_category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(new_category)
            db.session.commit()
            new_category_id = new_category.id

            expense = Expense(user_id=self.user_id,
                              date=date(2025, 5, 14), 
                              category_id=old_category_id, 
                              amount=20.5, 
                              description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        self.assertEqual(expense.category_id, old_category_id)
        payload = {"categoryId": new_category_id}
        print(payload)
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        with self.app.app_context():
            updated_expense = Expense.query.filter_by(id=expense_id, user_id=self.user_id).first()
            self.assertEqual(updated_expense.category_id, new_category_id)
        
    def test_update_expense_invalid_category(self):
        with self.app.app_context():
            old_category = Category(
                category="Dining",
                user_id=self.user_id,
            )
            db.session.add(old_category)
            db.session.commit()
            old_category_id = old_category.id

            expense = Expense(user_id=self.user_id,
                              date=date(2025, 5, 14), 
                              category_id=old_category_id, 
                              amount=20.5, 
                              description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        self.assertEqual(expense.category_id, old_category_id)
        
        non_existent_category_id = str(uuid.uuid4())
        self.assertNotEqual(non_existent_category_id, old_category_id)

        payload = {"categoryId": non_existent_category_id}
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn("Category not found", response.json["error"])

    def test_update_expense_amount(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(user_id=self.user_id,
                              date=date(2025, 5, 14), 
                              category_id=category_id, 
                              amount=20.5, 
                              description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id
            
        payload = {"amount": 100.82}
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        with self.app.app_context():
            updated_expense = Expense.query.filter_by(id=expense_id, user_id=self.user_id).first()
            self.assertEqual(float(updated_expense.amount), 100.82)

    def test_update_expense_invalid_amount(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(user_id=self.user_id,
                              date=date(2025, 5, 14), 
                              category_id=category_id, 
                              amount=20.5, 
                              description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id
            
        payload = {"amount": "invalid_amount"}
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(f"Invalid value for amount", response.json["error"])
    
    def test_update_expense_description(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(user_id=self.user_id,
                              date=date(2025, 5, 14), 
                              category_id=category_id, 
                              amount=20.5, 
                              description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"description": "Dinner"}
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} updated", response.json["message"])

        with self.app.app_context():
            updated_expense = Expense.query.filter_by(id=expense_id, user_id=self.user_id).first()
            self.assertEqual(updated_expense.description, "Dinner")

    def test_update_expense_invalid_description(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(user_id=self.user_id,
                              date=date(2025, 5, 14), 
                              category_id=category_id, 
                              amount=20.5, 
                              description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        payload = {"description": None}
        response = self.client.patch(
            f"/api/expense/{self.user_id}/expenses/{expense_id}", 
            data=json.dumps(payload), 
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(f"Invalid value for description", response.json["error"])

    def test_delete_expense(self):
        with self.app.app_context():
            category = Category(
                category="Restaurants",
                user_id=self.user_id
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id

            expense = Expense(user_id=self.user_id,
                              date=date(2025, 5, 14), 
                              category_id=category_id, 
                              amount=20.5, 
                              description="Lunch"
            )
            db.session.add(expense)
            db.session.commit()
            expense_id = expense.id

        response = self.client.delete(
            f"/api/expense/{self.user_id}/expenses/{expense_id}",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Expense {expense_id} deleted", response.json["message"])

if __name__ == "__main__":
    unittest.main()