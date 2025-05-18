from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'database', 'database.db')

class TestingConfig(Config):
    """Testing configuration."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use in-memory database for testing
    TESTING = True

# class ProductionConfig(Config):
#     """Production configuration."""
#     SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(basedir, 'database', 'database.db'))

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    # 'production': ProductionConfig
}

# Initialize extensions without binding them to the app
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(basedir, 'database'))

    from routes.expense import expense_blueprint
    from routes.category import category_blueprint
    app.register_blueprint(expense_blueprint, url_prefix="/expense")
    app.register_blueprint(category_blueprint, url_prefix="/category")

    return app