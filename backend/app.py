from flask import request, jsonify
from config import app, db
from models import Expense

@app.route("/expenses", methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    json_expenses = list(map(lambda x: x.to_json(), expenses))

    return jsonify({"expenses": json_expenses})

@app.route("/create_expense", methods=["POST"])
def create_expense():
    date = request.json.get("Date")
    category = request.json.get("Category")
    amount = request.json.get("Amount")
    description = request.json.get("Description")

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

    new_expense = Expense(date=date, category=category, amount=amount, description=description)
    try:
        db.session.add(new_expense)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "Expense created"}), 201


@app.route("/update_expense/<int:user_id>", methods=["PATCH"])
def update_expense(user_id):
    expense = Expense.query.get(user_id)

    if not expense:
        return jsonify({"message": "User not found"}), 404

    data = request.json

    expense.date = data.get("Date", expense.date)
    expense.category = data.get("Category", expense.category)
    expense.amount = data.get("Amount", expense.amount)
    expense.description = data.get("Description", expense.description)

    db.session.commit()

    return jsonify({"message": f"Expense {expense.id} updated"}), 200

@app.route("/delete_expense/<int:user_id>", methods=["DELETE"])
def delete_expense(user_id):
    expense = Expense.query.get(user_id)

    if not expense:
        return jsonify({"message": "Expense not found"}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": f"Expense {expense.id} deleted"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)