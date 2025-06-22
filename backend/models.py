from config import db
from datetime import datetime, UTC
import uuid

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(tz=UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(tz=UTC), onupdate=datetime.now(tz=UTC), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan', passive_deletes=True)
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan', passive_deletes=True)

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username
        }

class Category(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(tz=UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(tz=UTC), onupdate=datetime.now(tz=UTC), nullable=False)
    expenses = db.relationship('Expense', backref='category', lazy=True, passive_deletes=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', name='unique_category_per_user_constraint'),
    )

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "Category": self.category,
            "createdAt": self.created_at.isoformat(),
        }
    
class Expense(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.String, db.ForeignKey('category.id', ondelete='RESTRICT'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(tz=UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(tz=UTC), onupdate=datetime.now(tz=UTC), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "Date": self.date,
            "Category": self.category.category,
            "Amount": float(self.amount),
            "Description": self.description
        }