from config import db
    
# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     category = db.Column(db.String(80), nullable=False)
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    #category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    #category = db.relationship('Category', backref=db.backref('expenses', lazy=True))
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=False)

    def to_json(self):
        return {
            "Date": self.date,
            "Category": self.category,
            "Amount": self.amount,
            "Description": self.description
        }