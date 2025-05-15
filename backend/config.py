from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask
CORS(app)

app.config["SQLAlchemy_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SQLAlchemy_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)