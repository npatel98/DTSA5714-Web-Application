from flask import Blueprint, request, jsonify
from models import Category
from config import db

category_blueprint = Blueprint("category", __name__)

@category_blueprint.route("/categories", methods=['GET'])
def get_expenses():
    categories = Category.query.all()
    json_categories = list(map(lambda x: x.to_json(), categories))

    return jsonify({"expenses": json_categories})

@category_blueprint.route("/create_category", methods=["POST"])
def create_category():
    data = request.get_json()

    category = data.get('Category')
    new_category = Category(category=category)
    try:
        db.session.add(new_category)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "Category created"}), 201

@category_blueprint.route("/update_category/<int:category_id>", methods=["PATCH"])
def update_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"message": "Category not found"}), 404

    data = request.json
    category.category = data.get("Category", category.category)

    db.session.commit()

    return jsonify({"message": f"Category {category.id} updated"}), 200

@category_blueprint.route("/delete_category/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"message": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": f"Category {category.id} deleted"}), 200
