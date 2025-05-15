from config import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), unique=True, nullable=False)
    expenses = db.relationship('Expense', backref='category', lazy=True, passive_deletes=True)

    def to_json(self):
        return {
            "Category": self.category
        }
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='RESTRICT'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    def to_json(self):
        return {
            "Date": self.date,
            "Category": self.category_id.category,
            "Amount": float(self.amount),
            "Description": self.description
        }