from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_VERIFY_SUB = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    load_dotenv('.flaskenv')
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG')

    app = Flask(__name__)
    CORS(app)
    JWTManager(app)

    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(basedir, 'database'))

    from routes.expense import expense_blueprint
    from routes.category import category_blueprint
    from routes.auth import auth_blueprint
    app.register_blueprint(expense_blueprint, url_prefix="/api/expense")
    app.register_blueprint(category_blueprint, url_prefix="/api/category")
    app.register_blueprint(auth_blueprint, url_prefix="/api/auth")

    return app

# TODO: Set environment variables on AWS
    # In your AWS deployment environment (like Elastic Beanstalk or EC2), set these environment variables:
        # FLASK_CONFIG=production
        # DATABASE_URL=your-aws-rds-url (e.g., postgresql://username:password@host:port/dbname)