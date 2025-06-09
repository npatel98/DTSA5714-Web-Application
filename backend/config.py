from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL")

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("PRODUCTION_DATABASE_URL")

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG')

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

# TODO: Set environment variables on AWS
    # In your AWS deployment environment (like Elastic Beanstalk or EC2), set these environment variables:
        # FLASK_CONFIG=production
        # DATABASE_URL=your-aws-rds-url (e.g., postgresql://username:password@host:port/dbname)