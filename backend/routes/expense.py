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
    
    date = data.get("date")
    category_id = data.get("categoryId")
    amount = data.get("amount")
    description = data.get("description")

    if not date:
        return (
            jsonify({"message": "You must include a date"}),
            400,
        )
    
    if not category_id:
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

    new_expense = Expense(date=date, category_id=category_id, amount=amount, description=description)
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

    data = request.get_json()

    validators = {
        "date": lambda v: datetime.strptime(v, "%Y-%m-%d").date(),
        "categoryId": lambda v: v if isinstance(v, int) else (_ for _ in ()).throw(TypeError),
        "amount": lambda v: float(v),
        "description": lambda v: v if isinstance(v, str) else (_ for _ in ()).throw(TypeError),
    }

    field_mapping = {
        "date": "date",
        "categoryId": "category_id",
        "amount": "amount",
        "description": "description",
    }

    for key, validator in validators.items():
        if key in data:
            try:
                value = validator(data[key])
                setattr(expense, field_mapping[key], value)
            except (ValueError, TypeError):
                return {"error": f"Invalid value for '{key}'."}, 400

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