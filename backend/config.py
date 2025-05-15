from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os

# Initialize extensions without binding them to the app
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    CORS(app)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'database', 'database.db')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(basedir, 'database'))

    from routes.expense import expense_blueprint
    app.register_blueprint(expense_blueprint, url_prefix="/api")

    return app