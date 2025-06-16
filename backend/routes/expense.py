from flask import Blueprint, request, jsonify
from models import Expense, Category
from config import db
from datetime import datetime, UTC
from flask_jwt_extended import jwt_required, get_jwt_identity

expense_blueprint = Blueprint("expense", __name__)

@expense_blueprint.route("/<user_id>/expenses", methods=['GET'])
@jwt_required()
def get_expenses(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    
    expenses = Expense.query.filter_by(user_id=user_id).all()
    json_expenses = list(map(lambda x: x.to_json(), expenses))
    return jsonify({"expenses": json_expenses})

@expense_blueprint.route("/<user_id>/expenses", methods=["POST"])
@jwt_required()
def create_expense(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    
    data = request.get_json()
    
    date = data.get("date")
    category_id = data.get("categoryId")
    amount = data.get("amount")
    description = data.get("description")
    created_at = datetime.now(tz=UTC)
    updated_at = datetime.now(tz=UTC)

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

    new_expense = Expense(
        user_id=user_id, 
        date=date, 
        category_id=category_id, 
        amount=amount, 
        description=description, 
        created_at=created_at, 
        updated_at=updated_at)
    try:
        db.session.add(new_expense)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "Expense created"}), 201


@expense_blueprint.route("/<user_id>/expenses/<expense_id>", methods=["PATCH"])
@jwt_required()
def update_expense(user_id, expense_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403

    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    data = request.get_json()

    if "categoryId" in data:
        category = Category.query.filter_by(id=data["categoryId"], user_id=user_id).first()
        if not category:
            return jsonify({"error": "Category not found"}), 404

    validators = {
        "date": lambda v: datetime.strptime(v, "%Y-%m-%d").date(),
        "categoryId": lambda v: v if isinstance(v, str) else (_ for _ in ()).throw(TypeError),
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
                return {"error": f"Invalid value for {key}."}, 400

    db.session.commit()

    return jsonify({"message": f"Expense {expense.id} updated"}), 200

@expense_blueprint.route("/<user_id>/expenses/<expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(user_id, expense_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403
    
    expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": f"Expense {expense.id} deleted"}), 200