# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ondoc.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

from python.models import User, Doctor, Appointment, Feedback  # Import models here
from python.routes import *  # Import routes here

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user from the database