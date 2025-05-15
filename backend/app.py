from config import create_app, db
#from routes.expense import expense_blueprint

app = create_app()
#app.register_blueprint(expense_blueprint, url_prefix="/api")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)