from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# Create the Flask app
app = Flask(__name__)

# Set the app configuration variables
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy database instance
db = SQLAlchemy(app)

# Import the database models
from . import models

# Create the database tables
with app.app_context():
    db.create_all()
