from flask import Blueprint, request, jsonify
from models import Category
from config import db
from datetime import datetime, UTC
from flask_jwt_extended import jwt_required, get_jwt_identity

category_blueprint = Blueprint("category", __name__)

@category_blueprint.route("/<user_id>/categories", methods=['GET'])
@jwt_required()
def get_expenses(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403

    categories = Category.query.filter_by(user_id=user_id).all()
    json_categories = list(map(lambda x: x.to_json(), categories))
    return jsonify({"categories": json_categories})

@category_blueprint.route("/<user_id>/categories", methods=["POST"])
@jwt_required()
def create_category(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403

    data = request.get_json()
    category = data.get('Category')
    new_category = Category(
        category=category,
        user_id=user_id,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )
    try:
        db.session.add(new_category)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "Category created"}), 201

@category_blueprint.route("/<user_id>/categories/<category_id>", methods=["PATCH"])
@jwt_required()
def update_category(user_id, category_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"message": "Category not found"}), 404
    
    data = request.json
    category.category = data.get("Category", category.category)
    category.updated_at = datetime.now(tz=UTC)
    db.session.commit()

    return jsonify({"message": f"Category {category.id} updated"}), 200

@category_blueprint.route("/<user_id>/categories/<category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(user_id, category_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"message": "Unauthorized access"}), 403

    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({"message": "Category not found"}), 404
    
    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": f"Category {category.id} deleted"}), 200