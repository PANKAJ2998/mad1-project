from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()

from models.admin import Admin
from models.company import Company
from models.student import Student
from models.drive import PlacementDrive
from models.application import Application
