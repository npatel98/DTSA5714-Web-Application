from flask import Blueprint, request, jsonify
from models import Expense
from config import db
from datetime import datetime

expense_blueprint = Blueprint("expense", __name__)

@expense_blueprint.route("/expenses", methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    json_expenses = list(map(lambda x: x.to_json(), expenses))

    return jsonify({"expenses": json_expenses})

@expense_blueprint.route("/create_expense", methods=["POST"])
def create_expense():
    data = request.get_json()
    
    date = data.get("Date")
    category = data.get("Category")
    amount = data.get("Amount")
    description = data.get("Description")

    if not date:
        return (
            jsonify({"message": "You must include a date"}),
            400,
        )
    
    if not category:
        return (
            jsonify({"message": "You must include a category"}),
            400,
        )
    
    if not amount:
        return (
            jsonify({"message": "You must include an amount"}),
            400,
        )
    
    if not description:
        return (
            jsonify({"message": "You must include a description"}),
            400,
        )

    try:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

    new_expense = Expense(date=date, category_id=category, amount=amount, description=description)
    try:
        db.session.add(new_expense)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "Expense created"}), 201


@expense_blueprint.route("/update_expense/<int:expense_id>", methods=["PATCH"])
def update_expense(expense_id):
    expense = Expense.query.get(expense_id)

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    data = request.json

    expense.date = data.get("Date", expense.date)
    expense.category = data.get("Category", expense.category)
    expense.amount = data.get("Amount", expense.amount)
    expense.description = data.get("Description", expense.description)

    db.session.commit()

    return jsonify({"message": f"Expense {expense.id} updated"}), 200

@expense_blueprint.route("/delete_expense/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": f"Expense {expense.id} deleted"}), 200